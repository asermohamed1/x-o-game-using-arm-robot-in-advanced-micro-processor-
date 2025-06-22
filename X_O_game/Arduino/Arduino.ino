#include <Servo.h>

Servo bigAngleServo;
Servo babyAngleServo;
Servo rotationalServo;


int lastbabyAngle = 60; 
int lastrotationalAngle = 0;
int lastbigAngle = 0;





void verticalMove(int to = 0) {
    if (to > lastbabyAngle) 
        for (int i = lastbabyAngle;i <= to;i++) {
            babyAngleServo.write(i);
            delay(50);
        }
    else 
        for (int i = lastbabyAngle;i >= to;i--) { 
            babyAngleServo.write(i);
            delay(50);
        }
    lastbabyAngle = to;
}
  
void RotatinalMove(int to = 0) {
    if (to > lastrotationalAngle)
        for (int i = lastrotationalAngle;i <= to;i++) {
            rotationalServo.write(i);
            delay(50);
        }
    else 
        for (int i = lastrotationalAngle;i >= to;i--) {
            rotationalServo.write(i);
            delay(50);
        }
    lastrotationalAngle = to;
}
  
void HorizontalMove(int to = 0) {
    if (to > lastbigAngle) 
        for (int i = lastbigAngle;i <= to;i++) {
            bigAngleServo.write(i);
            delay(100);
        }
    else 
        for (int i = lastbigAngle;i >= to;i--) {
            bigAngleServo.write(i);
            delay(50);
        }
    lastbigAngle = to;
} 
  

int nextCubepos = 0;
int CubesPlaces[5][3] = {
    {82, 40 - 12, 10},
    {95, 45 - 12, 20}, 
    {107, 50 - 12, 25}, 
    {90, 20 - 12, 20},
    {100, 30 - 12, 20}
    // big - rotational - baby
};

void GetNextCube() {
    verticalMove(80);
    RotatinalMove(CubesPlaces[nextCubepos][1]);
    HorizontalMove(CubesPlaces[nextCubepos][0]);
    verticalMove(CubesPlaces[nextCubepos][2]); 
    verticalMove(80);
    nextCubepos++;
    if (nextCubepos >= 5) nextCubepos = 0; 
}

// big        - rotational - baby
// horizontal - rotational - vertical
void PutInPosition(int p1,int p2,int p3) {
    RotatinalMove(p2);
    HorizontalMove(p1);
    verticalMove(p3);  
    HorizontalMove(p1 - 15);
    verticalMove(80);
}




void moveInitalPlace() {
    babyAngleServo.write(60);
    delay(1000);
    rotationalServo.write(0);
    delay(1000);
    bigAngleServo.write(0);
    delay(1000);
    lastbabyAngle = 60; 
    lastrotationalAngle = 0;
    lastbigAngle = 0;
}



void setup() {
    Serial.begin(9600);
    bigAngleServo.attach(3);
    babyAngleServo.attach(9);
    rotationalServo.attach(6);
}

// big - rotational - baby
void moveArm(int angle1, int angle2, int angle3) {
  bigAngleServo.write(angle1);
  delay(1000);
  rotationalServo.write(angle2);
  delay(1000);
  babyAngleServo.write(angle3);
  delay(1000);
}




void loop() {
    moveInitalPlace();
    while(!Serial.available());
  
    String command = Serial.readStringUntil('\n');  // Read command
    command.trim();  // Remove spaces/newlines

    
    if (command == "top-left") {
        GetNextCube();
        PutInPosition(107,77 - 12,35);
        Serial.println("done");
    }
    else if (command == "top-center") {
        GetNextCube();
        PutInPosition(105,105 - 12,35);
        Serial.println("done");
    }
    else if (command == "top-right") {
        GetNextCube();
        PutInPosition(105,125 - 12,35);
        Serial.println("done");
    }
    else if (command == "middle-left") {
        GetNextCube();
        PutInPosition(80,75 - 12,35);
        Serial.println("done");
    }
    else if (command == "middle-center") {
        GetNextCube();
        PutInPosition(75,100 - 12,35);
        Serial.println("done");
    }
    else if (command == "middle-right") {
        GetNextCube();
        PutInPosition(78,130 - 12,35);
        Serial.println("done");
    }
    else if (command == "bottom-left") {
        GetNextCube();
        PutInPosition(60,60 - 12,20);
        Serial.println("done");
    }
    else if (command == "bottom-center") {
        GetNextCube();
        PutInPosition(55,100 - 12,20);
        Serial.println("done");
    }
    else if (command == "bottom-right") {
        GetNextCube();
        PutInPosition(55,140 - 12,20);
        Serial.println("done");
    }
    else if (command == "Reset") {
        nextCubepos = 0;
        Serial.println("done");
    }
}
