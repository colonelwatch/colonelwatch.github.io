---
layout: post
title: Playing with the VideoCore IV GPU on a Raspberry Pi Zero using VC4CL
---

Recently, I learned about [VC4CL](https://github.com/doe300/VC4CL), an implementation of OpenCL on the VideoCore IV, the GPU on every Raspberry Pi (except the Pi 4, which uses the VideoCore VI). The press about it seemed to talk about how it's been woefully underused in many projects, so I was naturally excited to use it myself. I was lately obsessed with making a fluid simulation toy, and I figured embedded GPGPU might be the answer.

I ended up picking the Raspberry Pi Zero for my project because it was small and cheap yet packing the same GPU, and I'm always attracted to running goliath things on David-like hardware.

To begin though, getting VC4CL on the Raspberry Pi Zero was a challenge to begin with--foreshadowing I didn't notice at the time. I followed this short and neat [guide](https://qengineering.eu/install-opencl-on-raspberry-pi-3.html), but I would wait *hours* just to see gcc getting killed at the linking stage every time. Some Googling revealed that this was an OOM (out-of-memory) kill, and the solution was a temporary swap space, according to StackOverflow. The below script makes sure to allocate that, so I guarantee that it works on a Raspberry Pi Zero.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install cmake git -y
sudo apt install ocl-icd-opencl-dev ocl-icd-dev -y
sudo apt install opencl-headers -y
sudo apt install clinfo -y
sudo apt install libraspberrypi-dev -y
sudo apt install clang clang-format clang-tidy -y
mkdir opencl
cd opencl
git clone https://github.com/doe300/VC4CLStdLib.git
git clone https://github.com/doe300/VC4CL.git
git clone https://github.com/doe300/VC4C.git

dd if=/dev/zero of=./tempswap count=1K bs=1M
mkswap ./tempswap
sudo chown root:root ./tempswap
sudo chmod 600 ./tempswap
sudo swapon ./tempswap

cd VC4CLStdLib
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
cd ../../VC4C
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
cd ../../VC4CL
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

cd ../..
sudo swapoff ./tempswap
sudo rm ./tempswap
```

After a couple more hours of compiling, I could finally confirm OpenCL functionality with `sudo clinfo` (sudo is necessary for all OpenCL applications on Raspberry Pi because the GPU is wired in with effectively privileged memory access, read the VC4CL repo for more information).

```console
pi@raspberrypi:~ $ sudo clinfo
Number of platforms                               1
  Platform Name                                   OpenCL for the Raspberry Pi VideoCore IV GPU
  Platform Vendor                                 doe300
  Platform Version                                OpenCL 1.2 VC4CL 0.4.9999 (2cf1d93)
  Platform Profile                                EMBEDDED_PROFILE
  Platform Extensions                             cl_khr_il_program cl_khr_spir cl_khr_create_command_queue cl_altera_device_temperature cl_altera_live_object_tracking cl_khr_icd cl_khr_extended_versioning cl_khr_spirv_no_integer_wrap_decoration cl_khr_suggested_local_work_size cl_vc4cl_performance_counters
  Platform Extensions function suffix             VC4CL

  Platform Name                                   OpenCL for the Raspberry Pi VideoCore IV GPU
Number of devices                                 1
  Device Name                                     VideoCore IV GPU
  Device Vendor                                   Broadcom
  Device Vendor ID                                0x14e4
  Device Version                                  OpenCL 1.2 VC4CL 0.4.9999 (2cf1d93)
  Driver Version                                  0.4.9999
  Device OpenCL C Version                         OpenCL C 1.2
  Device Type                                     GPU
  Device Profile                                  EMBEDDED_PROFILE
  Device Available                                Yes
  Compiler Available                              Yes
  Linker Available                                Yes
  Max compute units                               1
  Max clock frequency                             300MHz
  Core Temperature (Altera)                       31 C
  Device Partition                                (core)
    Max number of sub-devices                     0
    Supported partition types                     None
    Supported affinity domains                    (n/a)
  Max work item dimensions                        3
  Max work item sizes                             12x12x12
  Max work group size                             12
  Preferred work group size multiple              1
  Preferred / native vector sizes
    char                                                16 / 16
    short                                               16 / 16
    int                                                 16 / 16
    long                                                 0 / 0
    half                                                 0 / 0        (n/a)
    float                                               16 / 16
    double                                               0 / 0        (n/a)
  Half-precision Floating-point support           (n/a)
  Single-precision Floating-point support         (core)
    Denormals                                     No
    Infinity and NANs                             No
    Round to nearest                              No
    Round to zero                                 Yes
    Round to infinity                             No
    IEEE754-2008 fused multiply-add               No
    Support is emulated in software               No
    Correctly-rounded divide and sqrt operations  No
  Double-precision Floating-point support         (n/a)
  Address bits                                    32, Little-Endian
  Global memory size                              67108864 (64MiB)
  Error Correction support                        No
  Max memory allocation                           67108864 (64MiB)
  Unified memory for Host and Device              Yes
  Minimum alignment for any data type             64 bytes
  Alignment of base address                       512 bits (64 bytes)
  Global Memory cache type                        Read/Write
  Global Memory cache size                        32768 (32KiB)
  Global Memory cache line size                   64 bytes
  Image support                                   No
  Local memory type                               Global
  Local memory size                               67108864 (64MiB)
  Max number of constant args                     32
  Max constant buffer size                        67108864 (64MiB)
  Max size of kernel argument                     256
  Queue properties
    Out-of-order execution                        No
    Profiling                                     Yes
  Prefer user sync for interop                    Yes
  Profiling timer resolution                      1ns
  Execution capabilities
    Run OpenCL kernels                            Yes
    Run native kernels                            No
    IL version                                    SPIR-V_1.5 SPIR_1.2
    SPIR versions                                 1.2
  printf() buffer size                            0
  Built-in kernels                                (n/a)
  Device Extensions                               cl_khr_global_int32_base_atomics cl_khr_global_int32_extended_atomics cl_khr_local_int32_base_atomics cl_khr_local_int32_extended_atomics cl_khr_byte_addressable_store cl_nv_pragma_unroll cl_arm_core_id cl_ext_atomic_counters_32 cl_khr_initialize_memory cl_arm_integer_dot_product_int8 cl_arm_integer_dot_product_accumulate_int8 cl_arm_integer_dot_product_accumulate_int16 cl_arm_integer_dot_product_accumulate_saturate_int8 cl_khr_il_program cl_khr_spir cl_khr_create_command_queue cl_altera_device_temperature cl_altera_live_object_tracking cl_khr_icd cl_khr_extended_versioning cl_khr_spirv_no_integer_wrap_decoration cl_khr_suggested_local_work_size cl_vc4cl_performance_counters

NULL platform behavior
  clGetPlatformInfo(NULL, CL_PLATFORM_NAME, ...)  OpenCL for the Raspberry Pi VideoCore IV GPU
  clGetDeviceIDs(NULL, CL_DEVICE_TYPE_ALL, ...)   Success [VC4CL]
  clCreateContext(NULL, ...) [default]            Success [VC4CL]
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_DEFAULT)  Success (1)
    Platform Name                                 OpenCL for the Raspberry Pi VideoCore IV GPU
    Device Name                                   VideoCore IV GPU
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_CPU)  No devices found in platform
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_GPU)  Success (1)
    Platform Name                                 OpenCL for the Raspberry Pi VideoCore IV GPU
    Device Name                                   VideoCore IV GPU
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_ACCELERATOR)  No devices found in platform
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_CUSTOM)  No devices found in platform
  clCreateContextFromType(NULL, CL_DEVICE_TYPE_ALL)  Success (1)
    Platform Name                                 OpenCL for the Raspberry Pi VideoCore IV GPU
    Device Name                                   VideoCore IV GPU

ICD loader properties
  ICD loader Name                                 OpenCL ICD Loader
  ICD loader Vendor                               OCL Icd free software
  ICD loader Version                              2.2.12
  ICD loader Profile                              OpenCL 2.2
```

Just to test my concept, I reused most of the code from [ESP32-fluid-simulation](https://github.com/colonelatch/ESP32-fluid-simulation). Although the simulation used in that project was rather crude, I just wanted a low baseline to quickly begin with. In fact, I couldn't even get that to work. Sure, the numbers it yielded confirmed OpenCL worked, but it was strangely slow.

Over a weekend, I threw the kitchen sink at it: sacrificing accuracy, optimizing, and even overclocking. Still, to run 10 seconds of simulation at 30 FPS, the Raspberry Pi Zero took 16.982 seconds. Meanwhile, my Raspberry Pi 3--not overclocked and using the same GPU--ran the same code in 6.376 seconds. Considering that the Pi 3 was more than twice as fast, the *CPU* on the Zero was clearly too slow!

The entire simulation was running on the GPU, so why? Jacobi iteration. Each iteration was embarrassingly parallel by itself, but the next iteration was dependent on the previous. That meant each iteration meant a new kernel call in order to preserve the dependency, so I ended up needing to call *hundreds* of kernels per second. In fact, calling a kernel was quite expensive on the Zero's weak CPU. The algorithm itself--as parallel as it was--just wasn't parallel enough, and the Zero couldn't handle OpenCL's overhead as a result.

So, that meant that I should just pursue what I originally wanted on the Raspberry Pi 3; it's got a CPU powerful enough to handle the kernel calls. However, I *really* want the neat and tiny form factor of the Zero. What I might do instead is cellular automaton fluid. A technique used in some 2D games, it's not as mathematically rigorous as Eulerian fluid simulation, but it should require way less kernel calls. Anyway, I think it would be a fun exploration.

But I digress. I did succeed in using the Raspberry Pi Zero's GPU, though it went in a way I completely didn't expect. I think that VC4CL--and embedded GPGPU as a whole--can offer an unprecedented level of compute that enables projects that were unthinkable before. Eulerian fluid simulation on the Zero turned out to be too CPU-bound to prove it, but I'm determined to make a project that's really, *really* parallel and demonstrate.