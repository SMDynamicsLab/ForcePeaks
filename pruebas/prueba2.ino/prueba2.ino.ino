



boolean allow;  //CUANDO ALLOW ES FALSE, SE REGISTRA EL EVENTO DEL TRIAL
unsigned int isi=500;   //INICIALIZACIÓN DEL PERÍODO DEL ESTÍMULO, EL VALOR UTILIZADO SE RECIBE POR PYTHON.
unsigned int n_stim=5;  //Entiendo que son valores iniciales por las dudas //NO ENTIENDO BIEN PARA QUE SE USA ESTA VARIABLE, PARECIERA QUE PARA INDICAR CUÁL VA A SER EL NÚMERO TOTAL DE ESTÍMULOS
unsigned int stim_number;     //REGISTRA EL NÚMERO DE ESTÍMULO
//char message[] = "N5;I250;X";


//---------------------------------------------------------------------
//parse data from serial input
//input data format: eg "I500;n30;P-10;B15;T0;SR;FL;NB;A3;X"    //I500(Período del estímulo - isi = 500); N30(Número de estímulos - n_stim = 30); P-10(Tamaño de perturbación - perturb_size = -10);
void parse_data(char *line) {                                   //B15(Bip de perturbación (15-20) - perturb_bip = 15); T0(Tipo de perturbación - perturb_type = 0); SR(Estímulo por oído derecho - SR)
  char field[10];                                               //FL(Feedback por oído izquierdo - FL); NB(Ruido blanco por ambos oídos - NB); A3(Amplitud - amplitude = 3); 
  int n,data;                                                   //Desde Python: IOk, nOk, P(No usado), B(No usado), T(No usado), SOk, FOk, NOk, AOk. 
  //scan input until next ';' (field separator)
  while (sscanf(line,"%[^;]%n",field,&n) == 1) {
    data = atoi(field+1);
    //parse data according to field header
    switch (field[0]) {
      case 'I':
        isi = data;
        break;
      case 'N':
        n_stim = data;
        break;
        
      default:
        break;
    }
    line += n+1;
  }
  return;
}


//---------------------------------------------------------------------

void get_parameters() {
  char line[45];
  char i,aux;
  i = 0;

  //directly read next available character from buffer
  //if flow ever gets here, then next available character should be 'I'
  while (Serial.available() < 1) {}
  aux = Serial.read();
    
  //read buffer until getting an X (end of message)
  while (aux != 'X') {
  //keep reading if input buffer is empty
    while (Serial.available() < 1) {}
    line[i] = aux;
    i++;
    aux = Serial.read();
  }
  line[i] = '\0';         //terminate the string

//  //just in case, clear incoming buffer once read
//  Serial.flush();
  while(Serial.read()>=0);

  //parse input chain into parameters
  parse_data(line);
  Serial.println(line);
  return;
}



void setup() {

  Serial.begin(9600); //USB communication with computer
  allow = false;
  pinMode(LED_BUILTIN, OUTPUT);

}


void loop() {

  if(allow == false){   //ALLOW = FALSE, PERMITE QUE SE LEA UN MENSAJE DESDE PYTHON
//    //just in case, clear incoming buffer before starting trial
//    Serial.flush();
    while(Serial.read()>=0);

    get_parameters();   //LEE MENSAJE DE PYTHON DESDE EL SERIAL HASTA QUE ENCUENTRA UNA "X". EL ALGORITMO INTERPRETA LA "X" COMO FIN DE MENSAJE DESDE PYTHON. 
    allow = true;       //PONE EL FLAG ALLOW EN TRUE, PARA QUE NO SE LEA UN NUEVO DATO HASTA QUE NO SE PROCESE EL ACTUAL.
    stim_number = 0;    //INICIALIZA VARIABLE

  }
  else{               //ALLOW = TRUE, CORRE EL TRIAL ENVIADO EN EL MENSAJE DE PYTHON
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(isi);                      // wait for a second
    digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
    delay(isi);                      // wait for a second
    stim_number++;
    
    if (stim_number >= n_stim) {
      allow = false;
    }
  }
}
