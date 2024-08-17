#include <Wire.h>
#include <fix_fft.h>

// At the moment, the below are not user-configurable
#define SAMPLES 128
#define LOG_2_SAMPLES 7
#define COLUMNS 7
#define THRESHOLD 3

const uint8_t PROGMEM mapping_lut[SAMPLES/2] = {
  0, 0, 1, 1, 2, 2, 2, 3,
  3, 3, 3, 3, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 5, 5, 5,
  5, 5, 5, 5, 5, 5, 5, 5,
  5, 5, 5, 5, 5, 6, 6, 6,
  6, 6, 6, 6, 6, 6, 6, 6,
  6, 6, 6, 6, 6, 6, 6, 6,
  6, 6, 6, 6, 6, 6, 6, 6,
};

unsigned long current_time;

volatile int8_t sample_arr[SAMPLES];
volatile int sample_arr_index = 0;
volatile bool sample_arr_complete = false;

volatile uint8_t frame_count = 0;
volatile uint8_t output[COLUMNS] = {0};

uint8_t int_sqrt(uint16_t val){
  // Initial values if n = 0
  uint16_t Nsquared = 0;
  uint8_t twoNplus1 = 1;
  while(Nsquared <= val){
    Nsquared += twoNplus1;
    twoNplus1 += 2;
  }
  return twoNplus1/2 - 1;
}

void requestEvent(){
  Wire.write(output, COLUMNS);
}

ISR(TIMER1_OVF_vect){
  TCNT1 = 74;
  
  int sample = (ADC-512)/2; // scaling to fit 2Vpk-pk within 5V
  ADCSRA |= (1 << ADSC); // restart the ADC
  
  // we assume that the ADC is done because the interrupt freq is lower than sampling freq
  if(!sample_arr_complete){
    sample_arr[sample_arr_index] = sample;
    sample_arr_index++;
  }
  if(sample_arr_index == SAMPLES){
    sample_arr_index = 0;
    sample_arr_complete = true;
  }
}

void setup(){

  Wire.begin(9);
  Wire.onRequest(requestEvent);

  ADMUX &= ~((1 << REFS0) | (1 << REFS1) | (1 << REFS2)); // Vref == Vcc
  
  ADMUX &= ~((1 << MUX3) | (1 << MUX2) | (1 << MUX1) | (1 << MUX0));
  ADMUX |= (1 << MUX1); // Selects channel ADC2
  
  ADCSRA |= (1 << ADEN); // Turns on the ADC
  ADCSRA &= ~((1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0));
  ADCSRA |= (1 << ADPS2); // 1MHz ADC clock (about 60kHz sampling rate)

  ADCSRA |= (1 << ADSC); // Starts the first ADC conversion

  TCCR1 &= ~((1 << CS13) | (1 << CS12) | (1 << CS11) | (1 << CS10));
  TCCR1 |= (1 << CS11); // 8MHz Timer/Counter1 clock
  while(ADCSRA & (1 << ADSC)); // Busy-wait until the ADC is done
  TIMSK |= (1 << TOIE1); // Timer/Counter1 overflow interrupt
  TCNT1 = 74; // TCNT1 should always be preloaded with 74 for 44.1kHz
  
  while(!sample_arr_complete); // wait for enough samples to begin FFT

  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);
}

void loop(){
  int8_t real[SAMPLES], imag[SAMPLES];
  for(int i = 0; i < SAMPLES; i++){
    real[i] = sample_arr[i];
    imag[i] = 0;
  }
  sample_arr_complete = false;

  fix_fft(real, imag, LOG_2_SAMPLES, 0); // fix_fftr is broken

  // I believe the right way would be to add the magnitudes-squared, then isqrt the sum
  // but the attiny85 wasn't stable when i did that for some reason

  // the "wrong" way is below

  uint8_t raw_output[COLUMNS] = {0};
  for(int i = 0; i < SAMPLES/2; i++){
    uint8_t magnitude = int_sqrt((int16_t)real[i]*real[i]+(int16_t)imag[i]*imag[i]);
    if(magnitude < THRESHOLD) magnitude = 0; // cutting off noise

    // I used a LUT to combine the bins into exponential ranges, but there are
    //  alternatives than can be implemented using code (ex: if-else ladder).
    raw_output[pgm_read_byte_near(mapping_lut+i)] += magnitude; 
  }

  for(int i = 0; i < COLUMNS; i++) output[i] = raw_output[i];
}
