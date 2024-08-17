---
layout: post
title: On building real-time music spectrum visualizers using the FFT in Arduino
modified_date: 2023-05-19
excerpt: I've dedicated a lot of time to music visualization in Arduino (see my best work, [ESP32-oled-spectrum](https://github.com/colonelwatch/ESP32-oled-spectrum)). However, I've never elaborated on my thoughts and findings before, and it just ended up hidden in that project. Now, I figured, some people could probably benefit from it. **Yes**, an FFT can be run on a microcontroller, and you won't need the MSGEQ7 or a PC if you do this right. It's a bit informal (apologies), but here are three tips to get that running fast and at high resolution.
tags: [the Fast Fourier Transform (FFT)]
---

*The "MSGEQ7-killer" I promised was in-progress before I took my hiatus. I've now worked it into something barely functional (40 updates per sec with nil niceities), but the ATTiny85 proved slow and unstable. It didn't even have hardware multiplication. Working toward publishing wasn't worth it, but I'll leave the code [here](/assets/msgeq7-killer.ino) in case it helps someone.*

I've dedicated a lot of time to music visualization in Arduino (see my best work, [ESP32-oled-spectrum](https://github.com/colonelwatch/ESP32-oled-spectrum)). However, I've never elaborated on my thoughts and findings before, and it just ended up hidden in that project. Now, I figured, some people could probably benefit from it. **Yes**, an FFT can be run on a microcontroller, and you won't need the MSGEQ7 or a PC if you do this right. It's a bit informal (apologies), but here are three tips to get that running fast and at high resolution.

## 1. Carefully pick your FFT library

The most popular FFT library in the Arduino Library manager right now, [ArduinoFFT](https://github.com/kosme/ArduinoFFT), is most likely *not* the library you want to use. It has a very nice API, but it has a glaring problem: it uses the `double` data type. Almost all microcontrollers have no acceleration for the `double` type (the Teensy 4.0 is one exception), and this means `double` arithmetic is handled in software, slowly. As a result, picking a different library is generally *multiple times faster*, regardless of the microcontroller.

So which libraries should you use? Here are two libraries that I've tried with success and would recommend:

* fix_fft
    * There seem to be two versions of this on the internet, both for integers (fixed-point):
        * a [16-bit version](https://www.jjj.de/fft/fftpage.html) (see second entry) published in 2006, and
        * an [8-bit version](https://github.com/kosme/fix_fft) on Github that is available through the Arduino library manager.
    * The real FFT seems to be broken on both.
    * fix_fft implements the in-place form of the FFT. In-place algorithms can build their output inside the input's memory.
    * Both versions have an ambiguous license. It's impossible to legally integrate these into an open-source project without permission.
* [kissfft](https://github.com/mborgerding/kissfft)
    * It is configurable for 32-bit `float`s and 16-bit integers (32-bit integers seemed broken for me).
    * There is a working real FFT. A real FFT only works on real data (audio is), but it can run *twice* as fast!
    * kissfft implements the out-of-place form of the FFT. This means that you need to allocate extra memory for the FFT output.
    * Permissively MIT-licensed.

Considering kissfft, 32-bit `float`s offer the fastest and most accurate approach if you have the memory and an FPU. This was what I used in ESP32-oled-spectrum, but I've also seen that using the 16-bit integers mode can work instead. Considering fix_fft, it's one of the only 8-bit FFT libraries out there. You *could* use the 8-bit fix_fft to trade away even more accuracy for memory, but I myself would rather not be mired by licensing problems.

All said, definitely feel free to consider other libraries. For example, there are some [incredible](http://elm-chan.org/works/akilcd/report_e.html) [assembly](http://wiki.openmusiclabs.com/wiki/ArduinoFHT) routines out there that squeeze the most FFTs out of the atmega (NOT the attiny) architecture. The one by elm-chan is even permissively CC-BY-3.0 licensed.

### Addendum: Using kissfft

kissfft was originally written with PCs in mind. However, it's simple enough to use in embedded projects. Navigate to the kissfft repository, and pick out the following files: `kiss_fft.c`, `kiss_fft.h`, and `_kiss_fft_guts.h`. If you need the real FFT, also pick out the following files: `kiss_fftr.c` and `kiss_fftr.h`. Once you move these files into the source directory, you can include `kiss_fft.h` (or `kiss_fftr.h`) and call kissfft's functions like any other library. If you need the 16-bit integer version, you will need to compile with the option `-D FIXED_POINT=16`. Most embedded developers should be familiar with this.

However, Arduino doesn't nicely allow this, and it's not enough to just `#define` this before the include; you must create a file called `platform.local.txt` where `platform.txt` is located. This varies by the device you're compiling for, but good places to start looking are:

* `C:\Program Files (x86)\Arduino\hardware`
* `C:\Users\%USERPROFILE%\AppData\Local\Arduino15\packages`

For example, I've found `platform.txt` for my specific ESP32 compiler at `C:\Users\%USERPROFILE%\AppData\Local\Arduino15\packages\esp32\hardware\esp32\1.0.4`. The contents of `platform.local.txt` should be:

```
compiler.c.extra_flags= -D FIXED_POINT=16
compiler.c.elf.extra_flags=
compiler.S.extra_flags=
compiler.cpp.extra_flags= -D FIXED_POINT=16
compiler.ar.extra_flags=
compiler.objcopy.eep.extra_flags=
compiler.elf2hex.extra_flags=
```

## 2. Reuse old samples

One of my iterations ended up spending a majority of its time doing nothing. Why? It was waiting to collect enough samples to do an FFT on. Because it was spending so much time waiting, I was able to *double* its performance by just letting it reuse old samples. Were there consequences? Of course: old data now took time to disappear from the visualization. However, this was actually desirable because information tended to appear then disappear too quickly to be appreciated anyway. That is why other projects tend to apply exponential smoothing to the output, and reusing old data just happens to get part of the way there.

In my project, ESP32-oled-spectrum, I chose a length-6144 FFT because I wanted a very fine frequency resolution, but collecting 6144 samples at a sampling rate of 44100 Hz would have forced me to wait around 130 ms. That would've capped me at around 7 FFTs per second. Instead, I reused around *5836* samples in every FFT! As a result, I could push up to 120 FFTs per second. In practice, I built this using a circular buffer with a special feature that allowed me to read all past samples.

```c++
template <typename TYPE, int SIZE> class fftBuffer{
    public:
        void write(const TYPE *data, int w_size){
            int i_start = end_index;
            for(int j = 0, i = end_index; j < w_size; j++, i = (i+1)%SIZE) buffer[i] = data[j];
            end_index = (i_start+w_size)%SIZE;
        }
        void read(TYPE *data){
            int i_start = end_index-SIZE;
            if(i_start < 0) i_start += SIZE;
            for(int j = 0, i = i_start; j < SIZE; j++, i = (i+1)%SIZE) data[j] = buffer[i];
        }
        void alloc(){ buffer = (TYPE*)calloc(SIZE, sizeof(TYPE)); }
    private:
        TYPE *buffer;
        int end_index = 0;
};
```

## 3. Scale both frequency and magnitude logarithmically

This is how our ears perceive sound, so visualizations should scale the output of an FFT the same way. The magnitude is simple enough: we just need to convert all of the magnitudes to decibels. The reference level doesn't really matter because it's just the scaling we're after. Frequency, on the other hand, is tougher.

The output of an FFT is basically a histogram, revealing how much of the signal was in each "bin" of frequencies. However, all of these bins are of equal width--that's not logarithmic. Generally, the solution is to combine these bins into the columns of your spectrum visualizer. However, an unfortunate truth is that every new column with needs *exponentially* more bins than the last. For an exponential growth factor of 2, you would need 1 bin in the first range, 2 more bins in the second, 4 more in the third, going up to *64 more* bins in the seventh. In total, you would need 256 bins for just eight columns! However, if you allow a lot of rounding in the number of bins used, then you have the freedom to lower the growth factor to something more reasonable.

Empirically, I once had decent results with a growth factor that combined 1024 bins into 32 columns, though I forget what it was. That said, I have since switched to a more complex way to combine bins in ESP32-oled-spectrum: convolution kernels that turn an FFT into a Constant Q transform. Generally, it's more bin-inefficient, but it produces smooth handoffs between the columns. I leave the internal details to my other repo [cq_kernel](https://github.com/colonelwatch/cq_kernel). 

## Conclusion

So these are the insights that made ESP32-oled-spectrum, one of the fastest and highest-resolution music visualizers out there. I hope it helps anyone else who is interested in these kinds of things but refuses to settle for less like I did. ~~I might also consider demonstrating all these tips by making an MSGEQ7-killer, so click here if I ever end up doing that second part.~~