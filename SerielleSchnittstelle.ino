//Definiert die Pins, an denen Motor etc. an den Arduino angeschlossen werden


int dir = 2; //Direction Pin des Schrittmotors
int ste = 3; //Step Pin des Schrittmotors
int ena = 7;  //Enable Pin des Schrittmotors
int m1 = 8;  //Microstep1 Pin des Schrittmotors
int m2 = 9;  //Microstep2 Pin des Schrittmotors
int m3 = 10; //Microstep3 Pin des Schrittmotors
int R = 4; //Pin für den rechten Endschalter
int L = 5; //Pin für den linken Endschalter
int button = 6; //Pin für Hauptschalter


int usDelay = 2000; //Delay zwischen HIGH und LOW für einen Schritt in Mikrosekunden;


int k = 1; //Gibt Richtung an, kann 1 oder -1 sein
float pos = 0;
//int steps = 100; //Schritte, die in jede Richtung in jedem Loop gemacht werden
float schrittweite = 1;
float posL = 0.0;
float posR = 10; //140.0;

//Hauptschalterzeug
int  run = 1; //Gibt an, ob der Motor laufen darf, gegeben durch den Hauptschalter
bool ts = false; //Tasterstatus des Hauptschalters
bool tsL = false; //Tasterstatus des linken Endschalters
bool tsR = false; //Tasterstatus des rechten Endschalters
bool tsold = false; //Tasterstatus des Buttons in der letzten Iteration

//int val = 0;
//String s = "";
int n = 10; //Maximale Zeichenanzahl im Input

void setup() {
  Serial.begin(9600);
  pinMode(dir, OUTPUT);  //Die "Motor Steuerungs Pins" werden als Output Pins definiert
  pinMode(ste, OUTPUT); 
  pinMode(ena, OUTPUT);
  
  pinMode(L, INPUT); //Die Schalter Pins werden als Input Pins definiert
  pinMode(R, INPUT);
  pinMode(button, INPUT); 


  digitalWrite(ena, LOW); //Damit der Motor läuft, muss der Enable Pin LOW sein

  
  pinMode(m1, OUTPUT); //Die Microstep Pins werden als Output Pin definiert
  pinMode(m2, OUTPUT); 
  pinMode(m3, OUTPUT);

  //Vollschritt:        0 0 0
  //Halbschritt:        1 0 0
  //Viertelschritt:     0 1 0
  //Achtelschritt:      1 1 0
  //Sechzehntelschritt: 1 1 1
  
  digitalWrite(m1, LOW); //Mit der obigen Tabelle und diesen drei Zeilen kann eingestellt werden, was für Schritte (Microsteps) der Motor machen soll
  digitalWrite(m2, LOW);
  digitalWrite(m3, LOW);
}

//Setzt die Microsteps
void Vollschritt() {
  digitalWrite(m1, LOW);
  digitalWrite(m2, LOW);
  digitalWrite(m3, LOW);
}

void Halbschritt() {
  digitalWrite(m1, HIGH);
  digitalWrite(m2, LOW);
  digitalWrite(m3, LOW);
}

void Viertelschritt() {
  digitalWrite(m1, LOW);
  digitalWrite(m2, HIGH);
  digitalWrite(m3, LOW);
}

void Achtelschritt() {
  digitalWrite(m1, HIGH);
  digitalWrite(m2, HIGH);
  digitalWrite(m3, LOW);
}

void Sechzehntelschritt() {
  digitalWrite(m1, HIGH);
  digitalWrite(m2, HIGH);
  digitalWrite(m3, HIGH);
}

bool go(int steps) { //Diese Methode lässt den Motor steps (Mikro)Schritte gehen, das Vorzeichen entscheidet über die Richtung
  bool allowed = true;
  int i=0;
  k = steps/abs(steps); //Richtung, 1 oder -1
  if(k==1) {
    digitalWrite(dir, HIGH); //Die Drehrichtung wird eingestell, Uhrzeigersinn CW
  } else {
    digitalWrite(dir, LOW); //Die Drehrichtung wird eingestellt, Gegen den Uhrzeigersinn CCW
  }
  while(allowed && i < abs(steps)) {
    allowed = check_LR();
    i++;
  }
  if(!allowed) {
    Serial.println("Weg wurde durch Schalter beendet");
  }
  return allowed;
}


bool check_LR() { //Diese Funktion überprüft, ob die Endschalter gedrückt sind, oder ob sich der Motor noch weiter drehen darf
  bool allowed = false;
  tsL = digitalRead(L); //Tasterstatus des linken bzw. rechten Endschalters
  tsR = digitalRead(R);
  ts  = digitalRead(button); //Der Tasterstatus des Hauptschalters wird festgestellt
  if(ts==true && tsold==false) { //Wenn der Taster gerade (im Vergleich zur letzten Überprüfung) geschlossen wurde, dann wird run geändert 
                                 //Der Taster muss also gedrückt werden, um zu ändern, ob der Motor sich drehen darf
                                 //Da der Tasterstatus allerdings vgl.weise selten geprüft wird, muss der Taster lange gedrückt werden
    run *= -1;
  }
  tsold = ts;
  if (run == 1) { //Darf sich nur drehen, wenn der Hauptschalter das erlaubt
    
    if(k == 1 && tsR) { //Der Motor darf sich nur nach rechts drehen, wenn der rechte Endschalter es erlaubt
      do_step();
      pos += schrittweite;
      allowed = true;
    }
    if(k == -1 && tsL) { //Der Motor darf sich nur nach rechts drehen, wenn der rechte Endschalter es erlaubt
      do_step();
      pos -= schrittweite;
      allowed = true;
    } 
   }
   return allowed;    
}

void do_step() { //Führt einen Schritt (bzw. Microstep) durch
    digitalWrite(ste, HIGH);
    delayMicroseconds(usDelay);
    digitalWrite(ste, LOW);
    delayMicroseconds(usDelay);  
}

void loop() {

  if(Serial.available()==0) {
    //Serial.println("nichts");
  } else {
    String s = Serial.readString();
    Serial.print("Input = ");
    Serial.println(s);

    char a[n];
    s.toCharArray(a, n);

    
    if(a[0] == 'L') {
      Serial.println("\n going to L");
      bool allowed = true;
      int steps = -100/schrittweite;
      while(allowed) {
        allowed = go(steps);
      }
      
    } else if (a[0] == 'R') {
      Serial.println("\n going to R");
      bool allowed = true;
      int steps = 100/schrittweite;
      while(allowed) {
        allowed = go(steps);
      }
    } else if (a[0] == 'p' && a[1] == 'o' && a[2] == 's') {
      Serial.print("Position: ");
      Serial.println(pos);
    } else if (a[0] == 'n') {
      pos = 0;
      Serial.print("Position: ");
      Serial.println(pos);

    } else if(a[0] == 'm') {
      if(a[1] == '1') {
        if(a[2] == '6') {
          Sechzehntelschritt();
          schrittweite = 1.0/16.0;
          Serial.println("\n 1/16 Schritte");
        } else {
          Vollschritt();
          schrittweite = 1.0;
          Serial.println("\n ganze Schritte");
        }
      } else if(a[1] == '2') {
        Halbschritt();
        schrittweite = 0.5;
          Serial.println("\n 1/2 Schritte");
      } else if(a[1] == '4') {
        Viertelschritt();
        schrittweite = 0.25;
          Serial.println("\n 1/4 Schritte");
      } else if(a[1] == '8') {
        Achtelschritt();
        schrittweite = 0.125;
          Serial.println("\n 1/8 Schritte");
      }
    
    } else if (a[0] == 'a') {
      digitalWrite(ena, LOW);
    } else if (a[0] == 'd') {
      digitalWrite(ena, HIGH);
    } else if (a[0] == 'r' && a[1] == 'u' && a[2] == 'n') {
      Serial.println("run = 1");
      run = 1;
    } else {
      Serial.print("\n Ziel (Schritte): ");
      Serial.println(s);
      Serial.print("\n Start: ");
      Serial.println(pos);
      int steps = s.toInt()/schrittweite;
      go(steps);  
      Serial.print("Ende: ");
      Serial.println(pos);
    }


  }
}


  

  
