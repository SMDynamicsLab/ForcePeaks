//Código para Arduino MEGA
//Los primeros tiempo1000HZ ms del tap los registra a 1 kHz y los siguientes tiempo500HZ a 0.5 kHz).
//También mide tiempo de estímulo, tiempo de respuesta y calcula asincronías.
//va con dedoMunecaCodo_1sensor.m
//Va con estímulo y feedback no cuadrados. No usa la librería Tone. Usa el formato del código trialSimulator_sine.ino que es una adaptacin del codigo de Van Vugt fsr_tone_cont.ino

//El arduino ejecuta una única condición. 
//El MATLAB envía el período
//Desde Matlab, se puede elegir sin feedback, tapping_mode=1; o con feedback, tapping_mode=2
//Está pesado para que el MATLAB le mande NStim =27 taps, perturb_bip=15 (dummy variable) siempre y perturb_size=0 siempre (series isócronas).
//Registra la fuerza de tapsPrePertToBeRecorded taps previos al perturb_bip, registra la fuerza del perturb_bip y la de los tapsPosPertToBeRecordedtaps siguientes. Total de taps por trial en los que registra fuerza: 20.

//////////////////
//Pins
//stim Pin=11
//feedback Pin=7
//sensor Pin=A5

/////////////////////////////////////////////////
//Librerías
#include <stdlib.h> //ES para poder usar sprintf
//#include <Tone.h>
#include <avr/pgmspace.h> 

/////////////////////////////////////////////////
//Pines

int sensorIzqPin=A5;    //sensor de la izquierda
//#define sensorDerPin 7   //sensor de la derecha
//#define feedbackPin 12   //response feedback output to pin 12
//#define stimPin 11  //stimulus output to pin 13


/////////////////////////////////////////////////
//Variables

////Constantes
#define stimDuration 50        //stimulus duration (milliseconds)
#define feedbackDuration 50
//#define antiBounce (0.5*isi)   //minimum interval between responses (milliseconds)
#define isochronous 1          //code for perturbation type
#define stepChange 2
#define phaseShift 3



////Trial parameters
unsigned long t_micros;
unsigned int isi;
unsigned int perturbBip = 0;
unsigned int eventType = stepChange;
int perturbSize = 0;
int tappingMode = 0;
boolean feedbackOn = true;
boolean trialOn = false;
boolean perturbationDone = false;
boolean stimOn = false;
boolean respOn = false;
unsigned int antiBounce;

////Sensor
//Tone stim_tone, resp_tone;
//Cantidad de taps cuya fuerza registra: tapsPrePertToBeRecorded + tapsPosPertToBeRecorded + 1 (el +1 es por el tap de la perturbación)
unsigned int tapsPrePertToBeRecorded = 9; //cantidad de taps previos a la perturbaci'on en los que el sensor registra la fuerza
unsigned int tapsPosPertToBeRecorded = 15; //cantidad de taps despu'es de la perturbaci'on en los que el sensor registra la fuerza
int i = 0;
int voltajeSensorIzq;
//int voltajeSensorDer;
unsigned int NStim;
unsigned int stimNumber = 1;
unsigned int respNumber = 1;
unsigned long t;
unsigned long prevStim_t = 0;
unsigned long prevResp_t = 0;
unsigned long perturbBip_t;
unsigned voltajeSampleCounter = 0;
unsigned long prevVoltajeSample_t = 0;
unsigned int *voltajeSensor;
int sensorThreshold = 50;
boolean voltajeSensorIzq_flag = false;
//boolean voltajeSensorDer_flag = false;
boolean readVoltajeSensorOn = false;
boolean dosMuestrasXmili_flag = false;
//Duración del Tap. La cantidad total de milisegundos en los que el sensor registra la fuerza es: "tiempo1000HZ" + "tiempo500HZ"
int tiempo1000HZ=20; //milisegundos luego del tap en los que el sensor registra con una frecuencia de sampleo de 1KHz 
int tiempo500HZ=160; //milisegundos luego del finalizado tiempo1000 en los que el sensor registra con una frecuencia de sampleo de 500 Hz  


////Store data in memory
char *eventName;
unsigned int *eventNumber;
unsigned long *eventTime;
unsigned int eventCounter = 0;

////Communication with Matlab
char message[20];



/////////////////////////////////////////////////
//Funciones

////print a line avoiding "carriage return" of Serial.println()
void serialPrintString(char *string) {
  Serial.print(string);
  Serial.print("\n");
  return;
}


////parse data from serial input
//////input data format: eg "I%d;N%d;P%d;B%d;E%d;M%d;T%d;X"
void parseData(char *line) {

  char field[10];
  int n, data;
  //scan input until next ';' (field separator)
  while (sscanf(line, "%[^;]%n", field, &n) == 1) {
    data = atoi(field + 1);
    //parse data according to field header
    switch (field[0]) {
      case 'I':
        isi = data;
        break;
      case 'N':
        NStim = data;
        break;
      case 'P':
        perturbSize = data;
        break;
      case 'B':
        perturbBip = data;
        break;
      case 'E':
        eventType = data;
        break;
      case 'M':
        tappingMode = data;
        break;
      case 'T':
        sensorThreshold = data;
        break;
      default:
        break;

    }

    line += n;
    if (*line != ';')
      break;
    while (*line == ';')
      line++;
  }

  return;
}


////get keyword before reading parameters
void getKeyword() {
  boolean keywordReceived = false;
  char keyword[5] = "EEEE";

  //read input buffer until keyword "ARDU;"
  while (keywordReceived == false) {


    while (Serial.available() < 1) {

      //allow user to tap while waiting for data from computer
      if (feedbackOn == true) {
        voltajeSensorIzq = analogRead(sensorIzqPin);
        //voltajeSensorDer = analogRead(sensorDerPin);

        t = millis();
        if (voltajeSensorIzq  > sensorThreshold && respOn == false) {
          //resp_tone.play(NOTE_C5, feedbackDuration);
          tickOn();
          respOn = true;
          prevResp_t = t;
          voltajeSensorIzq = 0;
        }

        if (t - prevResp_t > feedbackDuration && respOn == true) {
          tickOff();
          respOn = false;
        }

/*
        if (voltajeSensorDer > sensorThreshold && respOn == false) {
          //resp_tone.play(NOTE_C6, feedbackDuration);
          tickOn3();
          respOn = true;
          prevResp_t = t;
          voltajeSensorDer = 0;
        }
*/
/*
        if (t - prevResp_t > feedbackDuration && respOn == true) {
          tickOff3();
          respOn = false;
        }
*/
      }
    }
    //read input buffer one at a time
    if (keyword[0] == 'A' && keyword[1] == 'R'
        && keyword[2] == 'D' && keyword[3] == 'U' && keyword[4] == ';') {
      //only combination allowed, in this specific order

      //Just in case
      respOn = false;
      tickOff3();

      prevResp_t = 0;
      //trialOn = true;
      keywordReceived = true;
    }

    else { //move buffer one step up
      keyword[0] = keyword[1];
      keyword[1] = keyword[2];
      keyword[2] = keyword[3];
      keyword[3] = keyword[4];
      keyword[4] = Serial.read();
    }

  }
  return;
}

////
void getParameters() {

  //wait until ARDU is received on the serial
  //getKeyword();

  char line[200], i, aux = '0';
  i = 0;

  //directly read next available character from buffer
  //if flow ever gets here, then next available character should be 'I'
  aux = Serial.read();

  //read buffer until getting an X (end of message)
  while (aux != 'X') {
    //keep reading if input buffer is empty
    while (Serial.available() < 1) {}
    line[i] = aux;
    i++;
    aux = Serial.read();
  }

  line[i] = '\0';					//terminate the string

  //just in case, clear incoming buffer once read
  Serial.flush();


  //parse input chain into parameters
  parseData(line);

  //Set trial conditions
  if (tappingMode == 1) {
    feedbackOn = false;
  }
  else  {
    feedbackOn = true;
  }


  // wait for ARDU to start the trial
  //getKeyword();

  return;
}


/////////////////////////////////////////////////
//Setup

void setup() {
  //  stim_tone.begin(stimPin);    //stimulus output
  //  resp_tone.begin(feedbackPin);   //feedback output

  Serial.begin(115200);
  //Serial.begin(9600);
  //pinMode(sensorIzqPin, INPUT);
  //pinMode(sensorDerPin, INPUT);
  pinMode(51, OUTPUT); //LED de prueba
  digitalWrite(51,LOW);
  //  pinMode(stimPin, OUTPUT);
  //  pinMode(feedbackPin, OUTPUT);
  trialOn = false;

  // Initialise fast PWM
  initPWM(); //timer 1
  initPWM3(); //timer 3

  // Set phase increment according to
  // desired OFF frequency
  tickOff(); //timer 1
  tickOff3();  // timer 3

  // Enable global interrupts
  sei();



}


/////////////////////////////////////////////////
//Loop

//main loop
void loop() {

  if (trialOn == false) {

    //get trial parameters
    //getParameters();

    getKeyword(); //espera "ARDU;" , mientras tanto permite feedback o no, según la condición del último trial
    getParameters(); //cuando recive "ARDU;" va a buscar los parámetros del trial (isi NStim pertubBip perturbSize tappingMode eventType sensorThreshold)
    getKeyword(); //espera nuevamente "ARDU;"
    antiBounce=isi*.67; //para un ISI de 600 ms corresponde a un antibounce de 400

    //Esto es para que no sature la memoria. 
    if (NStim <= 32) {
      eventName = (char*) calloc(3 * NStim, sizeof(char));
      eventNumber = (unsigned int*) calloc(3 * NStim, sizeof(unsigned int));
      eventTime = (unsigned long*) calloc(3 * NStim, sizeof(unsigned long));
    }
    else  {
      eventName = (char*) calloc(3 * 32, sizeof(char));
      eventNumber = (unsigned int*) calloc(3 * 32, sizeof(unsigned int));
      eventTime = (unsigned long*) calloc(3 * 32, sizeof(unsigned long));
    }

    voltajeSensor = (unsigned int*) calloc(3000, sizeof(unsigned int));  //   taps seguro, quizás más

    trialOn = true;
  }

  //start trial
  else if (trialOn == true) {
    t = millis();

    //turn on stimulus
    if ((t - prevStim_t) >= isi && stimNumber <= NStim && stimOn == false) {
      //stim_tone.play(NOTE_C5,stimDuration);
      tickOn();
      stimOn = true;
      //store event data
      eventName[eventCounter] = 'S';
      eventNumber[eventCounter] = stimNumber;
      eventTime[eventCounter] = t;
      //next step
      eventCounter++;
      stimNumber++;
      prevStim_t = t;
    }

    //turn off stimulus
    if (t - prevStim_t > stimDuration && stimOn == true) { //apaga el tono estimulo
      tickOff();
      stimOn = false;
    }


    ////read response and fisrt contact actions
    if ((t - prevResp_t) > antiBounce) {

      voltajeSensorIzq = analogRead(sensorIzqPin);    // read the input pin
      //voltajeSensorDer = analogRead(sensorDerPin);

      if (voltajeSensorIzq > sensorThreshold) { //sensor de la izquierda
        if (feedbackOn == true) {
          //resp_tone.play(NOTE_C7,feedbackDuration);
          tickOn3();
          respOn = true;
        }

        //store event data
        eventName[eventCounter] = 'I';  //'I'. Respuesta proveniente del sensor de la izquierda.
        eventNumber[eventCounter] = respNumber;
        eventTime[eventCounter] = t;
        //next step
        respNumber++;
        eventCounter++;
        prevResp_t = t;
        voltajeSensorIzq = 0;
        voltajeSensorIzq_flag = true;
      }

/*
      if (voltajeSensorDer > sensorThreshold) {  //sensor de la derecha
        if (feedbackOn == true) {
          //resp_tone.play(NOTE_C7,feedbackDuration);
          tickOn3();
          respOn = true;
        }

        //store event data
        eventName[eventCounter] = 'D'; //Respuesta proveniente del sensor de la derecha.
        eventNumber[eventCounter] = respNumber;
        eventTime[eventCounter] = t;
        //next step
        respNumber++;
        eventCounter++;
        prevResp_t = t;
        voltajeSensorDer = 0;
        voltajeSensorDer_flag = true;
      }
*/

    }

    //tur off feedback
    if (t - prevResp_t > feedbackDuration && respOn == true) {
      tickOff3();
      respOn = false;
    }


    /////Read sensor voltaje


    //Sensor. Intervalo de taps en el que la lectura del sensor está habilitada.
    if (stimNumber > (perturbBip - (tapsPrePertToBeRecorded + 1)) && (t - prevStim_t) >= (isi / 2)) { //el sensor es habilitado para registrar cuando faltan tapsPrePertToBeRecorded taps para la perturbación
      readVoltajeSensorOn = true;
    }

    //if (stimNumber > (perturbBip + 14) && (t - prevStim_t) >= (isi / 2)) { //el sensor se deshabilita 14 taps y medio después de la perturbación 
    //if (stimNumber > (perturbBip + 8) && (t - prevStim_t) >= (isi / 2)) { //el sensor se deshabilita 8 taps y medio después de la perturbación. Usar con NStim=23 en Matlab. Registra la fuerza de 16 taps
      if (stimNumber > (perturbBip + tapsPosPertToBeRecorded) && (t - prevStim_t) >= (isi / 2)) { //el sensor se deshabilita 12 taps y medio después de la perturbación. Usar con NStim=27 en Matlab. Registra la fuerza de 20 taps 
      readVoltajeSensorOn = false;
    }


    //1kHz sampling

    if ((t - prevVoltajeSample_t) >= 1 && voltajeSensorIzq_flag == true && readVoltajeSensorOn == true && dosMuestrasXmili_flag == false) { //almacena el valor de entrada del sensor, un dato por milisegundo
      voltajeSensor[voltajeSampleCounter] = analogRead(sensorIzqPin);
      //tiempo[osc_counter]=t;
      voltajeSampleCounter++;
      prevVoltajeSample_t = t;
    }
/*
    if ((t - prevVoltajeSample_t) >= 1 && voltajeSensorDer_flag == true && readVoltajeSensorOn == true && dosMuestrasXmili_flag == false) { //almacena el valor de entrada del sensor, un dato por milisegundo
      voltajeSensor[voltajeSampleCounter] = analogRead(sensorDerPin);
      //tiempo[osc_counter]=t;
      voltajeSampleCounter++;
      prevVoltajeSample_t = t;
    }
*/

/*
    //Stop sampling at 1KHz
    if ((t - prevResp_t) >= 50 && (voltajeSensorIzq_flag == true || voltajeSensorDer_flag == true ) && readVoltajeSensorOn == true && dosMuestrasXmili_flag == false) { //intervalo de tiempo durante el cual el sensor registra cada tap  (50 ms)
      voltajeSensor[voltajeSampleCounter] = 1800; //terminador. Cuando cambia la frecuencia de muestreo
      voltajeSampleCounter++;
      //voltajeSensorIzq_flag = false;
      //voltajeSensorDer_flag = false;
      dosMuestrasXmili_flag = true;
    }
*/

//Stop sampling at 1KHz
    if ((t - prevResp_t) >= tiempo1000HZ && (voltajeSensorIzq_flag == true) && readVoltajeSensorOn == true && dosMuestrasXmili_flag == false) { //intervalo de tiempo durante el cual el sensor registra cada tap  (50 ms)
      voltajeSensor[voltajeSampleCounter] = 1800; //terminador. Cuando cambia la frecuencia de muestreo
      voltajeSampleCounter++;
      //voltajeSensorIzq_flag = false;
      //voltajeSensorDer_flag = false;
      dosMuestrasXmili_flag = true;
    }
    
    //0.5 kHz sampling
    if ((t - prevVoltajeSample_t) >= 2 && voltajeSensorIzq_flag == true && readVoltajeSensorOn == true && dosMuestrasXmili_flag == true) { //almacena el valor de entrada del sensor, un dato por milisegundo
      voltajeSensor[voltajeSampleCounter] = analogRead(sensorIzqPin);
      //tiempo[osc_counter]=t;
      voltajeSampleCounter++;
      prevVoltajeSample_t = t;
    }

/*
    if ((t - prevVoltajeSample_t) >= 2 && voltajeSensorDer_flag == true && readVoltajeSensorOn == true && dosMuestrasXmili_flag == true) { //almacena el valor de entrada del sensor, un dato por milisegundo
      voltajeSensor[voltajeSampleCounter] = analogRead(sensorDerPin);
      //tiempo[osc_counter]=t;
      voltajeSampleCounter++;
      prevVoltajeSample_t = t;
    }
*/
  
    /*
    //Stop 0.5 kHz sampling
    if ((t - prevResp_t) >= 200 && (voltajeSensorIzq_flag == true || voltajeSensorDer_flag == true ) && readVoltajeSensorOn == true && dosMuestrasXmili_flag == true) { //toma 1 muestra cada 2 ms desde los 50 ms hasta los 200 ms
      voltajeSensor[voltajeSampleCounter] = 2000; //terminador. Cuando cambia la frecuencia de muestreo
      voltajeSampleCounter++;
      voltajeSensorIzq_flag = false;
      voltajeSensorDer_flag = false;
      dosMuestrasXmili_flag = false;
    }
*/
    //Stop 0.5 kHz sampling
    if ((t - prevResp_t) >= (tiempo1000HZ+tiempo500HZ) && (voltajeSensorIzq_flag == true) && readVoltajeSensorOn == true && dosMuestrasXmili_flag == true) { //toma 1 muestra cada 2 ms desde los 50 ms hasta los 200 ms
      voltajeSensor[voltajeSampleCounter] = 2000; //terminador. Cuando cambia la frecuencia de muestreo
      voltajeSampleCounter++;
      voltajeSensorIzq_flag = false;
      //voltajeSensorDer_flag = false;
      dosMuestrasXmili_flag = false;
    }

    ////perturbation
    if (stimNumber == perturbBip && perturbationDone == false) {
      //step change or first perturbation of phase shift
      isi += perturbSize;
      perturbationDone = true;
      
    }
/*
//Prende LED
if (stimNumber == perturbBip +4 ) 
digitalWrite(51,HIGH);
*/

    ////end trial
    //allow one more period (without stimulus)
    if (stimNumber > NStim && (t - prevStim_t) >= isi) {
      tickOff3(); //detiene el timer 3 para evitar que quede sonando el feedback
      for (i = 0; i < eventCounter; i++) {
        sprintf(message, "%c %d: %ld;",
                eventName[i], eventNumber[i], eventTime[i]);
        serialPrintString(message);
      }

      Serial.println("E");	//send READY message

      for (i = 0; i < voltajeSampleCounter; i++) { //send sensor data to Matlab
        // sprintf(message,"%d: %ld;",osc[i],tiempo[i]);           //%d decimal integer
        sprintf(message, "%d:", voltajeSensor[i]);         //%d decimal integer
        Serial.println(message);
      }

      Serial.println("F");  //send END message

      //Reset variables for next trial

      free(eventName);
      free(eventNumber);
      free(eventTime);
      i = 0;
      prevVoltajeSample_t = 0;
      voltajeSampleCounter = 0;
      free(voltajeSensor);
      readVoltajeSensorOn = false;
      feedbackOn = true;
      prevStim_t = 0;
      prevResp_t = 0;
      stimNumber = 1;
      respNumber = 1;
      eventCounter = 0;
      trialOn = false;
      perturbationDone = false;
      digitalWrite(51,LOW);
    }

  }
}



/////////////////////////////////////////////////
//Tonos de estímulo y feedback (adaptación del código fsr_tone_cont.ino de Van Vugt y de trialSimulator_sine.ino)
//Estímulo: seno -timer 1 - pin 11
//Feedback: seno -timer 3 - pin 5



// variables for tone condition
int stimFreq = 495;//(C6) //1046.5; // defines the frequency (i.e., pitch) of the tone (in Hz)
int feedbackFreq = 1800;//(C6) //1046.5; // defines the frequency (i.e., pitch) of the tone (in Hz)


/////////////////////////////// Set up lookup table for waveform generation

static const uint8_t  sineTable[] PROGMEM =
{
  0x80, 0x83, 0x86, 0x89, 0x8c, 0x8f, 0x92, 0x95,
  0x98, 0x9c, 0x9f, 0xa2, 0xa5, 0xa8, 0xab, 0xae,
  0xb0, 0xb3, 0xb6, 0xb9, 0xbc, 0xbf, 0xc1, 0xc4,
  0xc7, 0xc9, 0xcc, 0xce, 0xd1, 0xd3, 0xd5, 0xd8,
  0xda, 0xdc, 0xde, 0xe0, 0xe2, 0xe4, 0xe6, 0xe8,
  0xea, 0xec, 0xed, 0xef, 0xf0, 0xf2, 0xf3, 0xf5,
  0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfc,
  0xfd, 0xfe, 0xfe, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfe, 0xfe,
  0xfd, 0xfc, 0xfc, 0xfb, 0xfa, 0xf9, 0xf8, 0xf7,
  0xf6, 0xf5, 0xf3, 0xf2, 0xf0, 0xef, 0xed, 0xec,
  0xea, 0xe8, 0xe6, 0xe4, 0xe2, 0xe0, 0xde, 0xdc,
  0xda, 0xd8, 0xd5, 0xd3, 0xd1, 0xce, 0xcc, 0xc9,
  0xc7, 0xc4, 0xc1, 0xbf, 0xbc, 0xb9, 0xb6, 0xb3,
  0xb0, 0xae, 0xab, 0xa8, 0xa5, 0xa2, 0x9f, 0x9c,
  0x98, 0x95, 0x92, 0x8f, 0x8c, 0x89, 0x86, 0x83,
  0x80, 0x7c, 0x79, 0x76, 0x73, 0x70, 0x6d, 0x6a,
  0x67, 0x63, 0x60, 0x5d, 0x5a, 0x57, 0x54, 0x51,
  0x4f, 0x4c, 0x49, 0x46, 0x43, 0x40, 0x3e, 0x3b,
  0x38, 0x36, 0x33, 0x31, 0x2e, 0x2c, 0x2a, 0x27,
  0x25, 0x23, 0x21, 0x1f, 0x1d, 0x1b, 0x19, 0x17,
  0x15, 0x13, 0x12, 0x10, 0x0f, 0x0d, 0x0c, 0x0a,
  0x09, 0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x03,
  0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
  0x02, 0x03, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
  0x09, 0x0a, 0x0c, 0x0d, 0x0f, 0x10, 0x12, 0x13,
  0x15, 0x17, 0x19, 0x1b, 0x1d, 0x1f, 0x21, 0x23,
  0x25, 0x27, 0x2a, 0x2c, 0x2e, 0x31, 0x33, 0x36,
  0x38, 0x3b, 0x3e, 0x40, 0x43, 0x46, 0x49, 0x4c,
  0x4f, 0x51, 0x54, 0x57, 0x5a, 0x5d, 0x60, 0x63,
  0x67, 0x6a, 0x6d, 0x70, 0x73, 0x76, 0x79, 0x7c
};

/*
  static const uint8_t  sineTable[] PROGMEM =
  {
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  };*/


/////////////////////////////// Set up lookup table for waveform generation

static const uint8_t  sineTable3[] PROGMEM =
{
  0x80, 0x83, 0x86, 0x89, 0x8c, 0x8f, 0x92, 0x95,
  0x98, 0x9c, 0x9f, 0xa2, 0xa5, 0xa8, 0xab, 0xae,
  0xb0, 0xb3, 0xb6, 0xb9, 0xbc, 0xbf, 0xc1, 0xc4,
  0xc7, 0xc9, 0xcc, 0xce, 0xd1, 0xd3, 0xd5, 0xd8,
  0xda, 0xdc, 0xde, 0xe0, 0xe2, 0xe4, 0xe6, 0xe8,
  0xea, 0xec, 0xed, 0xef, 0xf0, 0xf2, 0xf3, 0xf5,
  0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfc,
  0xfd, 0xfe, 0xfe, 0xff, 0xff, 0xff, 0xff, 0xff,
  0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfe, 0xfe,
  0xfd, 0xfc, 0xfc, 0xfb, 0xfa, 0xf9, 0xf8, 0xf7,
  0xf6, 0xf5, 0xf3, 0xf2, 0xf0, 0xef, 0xed, 0xec,
  0xea, 0xe8, 0xe6, 0xe4, 0xe2, 0xe0, 0xde, 0xdc,
  0xda, 0xd8, 0xd5, 0xd3, 0xd1, 0xce, 0xcc, 0xc9,
  0xc7, 0xc4, 0xc1, 0xbf, 0xbc, 0xb9, 0xb6, 0xb3,
  0xb0, 0xae, 0xab, 0xa8, 0xa5, 0xa2, 0x9f, 0x9c,
  0x98, 0x95, 0x92, 0x8f, 0x8c, 0x89, 0x86, 0x83,
  0x80, 0x7c, 0x79, 0x76, 0x73, 0x70, 0x6d, 0x6a,
  0x67, 0x63, 0x60, 0x5d, 0x5a, 0x57, 0x54, 0x51,
  0x4f, 0x4c, 0x49, 0x46, 0x43, 0x40, 0x3e, 0x3b,
  0x38, 0x36, 0x33, 0x31, 0x2e, 0x2c, 0x2a, 0x27,
  0x25, 0x23, 0x21, 0x1f, 0x1d, 0x1b, 0x19, 0x17,
  0x15, 0x13, 0x12, 0x10, 0x0f, 0x0d, 0x0c, 0x0a,
  0x09, 0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x03,
  0x02, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,
  0x02, 0x03, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
  0x09, 0x0a, 0x0c, 0x0d, 0x0f, 0x10, 0x12, 0x13,
  0x15, 0x17, 0x19, 0x1b, 0x1d, 0x1f, 0x21, 0x23,
  0x25, 0x27, 0x2a, 0x2c, 0x2e, 0x31, 0x33, 0x36,
  0x38, 0x3b, 0x3e, 0x40, 0x43, 0x46, 0x49, 0x4c,
  0x4f, 0x51, 0x54, 0x57, 0x5a, 0x5d, 0x60, 0x63,
  0x67, 0x6a, 0x6d, 0x70, 0x73, 0x76, 0x79, 0x7c
};



////////////////////////////////////  set PWM variables and functions
// PWM output (OCR1A)
int stimPin = 11;

// 16 bit accumulator
uint16_t phaseAccumulator = 0;
// 16 bit delta
uint16_t phaseIncrement = 0;
// DDS resolution
const uint32_t resolution =  68719;
// wavetable lookup index(upper 8 bits of the accumulator)
uint8_t index = 0;



// PWM output (OCR3A)
int feedbackPin3 = 5; //timer3 controls pins 2,3 and 5

// 16 bit accumulator
uint16_t phaseAccumulator3 = 0;
// 16 bit delta
uint16_t phaseIncrement3 = 0;
// DDS resolution
const uint32_t resolution3 =  68719;
// wavetable lookup index(upper 8 bits of the accumulator)
uint8_t index3 = 0;

// TIMER1 will overflow at a 62.5KHz(Sampling frequency).
// Updates the OCR1A value and the accumulator.
// Computes the next sample to be sent to the PWM.

ISR(TIMER1_OVF_vect)
{
  static uint8_t osc = 0;

  // Send oscillator output to PWM
  OCR1A = osc;

  // Update accumulator
  phaseAccumulator += phaseIncrement;
  index = phaseAccumulator >> 8;

  // Read oscillator value for next interrupt
  osc = pgm_read_byte( &sineTable[index] );

}

// TIMER3 will overflow at a 62.5KHz(Sampling frequency).
// Updates the OCR1A value and the accumulator.
// Computes the next sample to be sent to the PWM.
ISR(TIMER3_OVF_vect)
{
  static uint8_t osc3 = 0;

  // Send oscillator output to PWM
  OCR3A = osc3;

  // Update accumulator
  phaseAccumulator3 += phaseIncrement3;
  index3 = phaseAccumulator3 >> 8;

  // Read oscillator value for next interrupt
  osc3 = pgm_read_byte( &sineTable3[index3] );

}

// Configures TIMER1 to fast PWM non inverted mode.
// Prescaler set to 1, which means that timer overflows
// every 16MHz/256 = 62.5KHz
void initPWM(void)
{
  // Set PORTB1 pin as output
  pinMode(stimPin, OUTPUT);

  // 8-bit Fast PWM - non inverted PWM
  TCCR1A = _BV(COM1A1) | _BV(WGM10);

  // Start timer without prescaler
  TCCR1B = _BV(CS10) | _BV(WGM12);

  // Enable overflow interrupt for OCR1A
  TIMSK1 = _BV(TOIE1);

}

// Configures TIMER3 to fast PWM non inverted mode.
// Prescaler set to 1, which means that timer overflows
// every 16MHz/256 = 62.5KHz
void initPWM3(void)
{
  // Set PORTB1 pin as output
  pinMode(feedbackPin3, OUTPUT);

  // 8-bit Fast PWM - non inverted PWM
  TCCR3A = _BV(COM3A1) | _BV(WGM30);

  // Start timer without prescaler
  TCCR3B = _BV(CS30) | _BV(WGM32);

  // Enable overflow interrupt for OCR1A
  TIMSK3 = _BV(TOIE3);

}

// Translates the desired output frequency to a phase
// increment to be used with the phase accumulator.
// The 16 bit shift is required to remove the  2^16
// scale factor of the resolution.
void setFrequency( uint16_t frequency )
{
  uint64_t phaseIncr64 =  resolution * frequency;
  phaseIncrement = phaseIncr64 >> 16;
}

void setFrequency3( uint16_t frequency3 )
{
  uint64_t phaseIncr643 =  resolution3 * frequency3;
  phaseIncrement3 = phaseIncr643 >> 16;
}

// The duration of one metronome tick (in microsec)
//const unsigned long TICKDURATION = tone_dur*1000;   // 20msec

// function to turn tick on
void tickOn() {
  setFrequency(stimFreq);
}

// function to turn tick on
void tickOn3() {
  setFrequency3(feedbackFreq);
}

// function to turn tick off
void tickOff() {
  setFrequency( .05 ); // so that you practically don't hear anything (well below perceptual limit of humans)
}

// function to turn tick off
void tickOff3() {
  setFrequency3( .05 ); // so that you practically don't hear anything (well below perceptual limit of humans)
}
