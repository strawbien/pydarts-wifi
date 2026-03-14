/* @file CustomKeypad.pde
|| @version 1.0
|| @author Alexander Brevig
|| @contact alexanderbrevig@gmail.com
||
|| @description
|| | Demonstrates changing the keypad size and key values.
|| #
*/
/*#include <Keypad.h>
*/
/* 
Note : This file should be adapted to your the wires that you havec connected to your arduino controler !
*/
const byte numRows = 8; //four rows
const byte numCols = 8; //four columns
const int debounceTime = 100;//100 works better than great ! (20 was also a good choice)
//define the cymbols on the buttons of the keypads
char keymap[numRows][numCols] = {
  {'0','1','2','4','5','6','7','8'},
  {'a','b','c','d','e','f','g','h'},
  {'j','k','l','m','n','o','p','q'},
  {'s','t','u','v','w','x','y','z'},
  {'B','C','D','E','F','G','H','I'},
  {'K','L','M','N','O','P','Q','R'},
  {'T','U','V','W','X','Y','Z','+'},
  {'*','/','?','!','&','$','@','#'}
};
byte rowPins[numRows] = {A0, A1, A2, A3, A4, A5, A6, A7}; //connect to the row pinouts of the keypad
byte colPins[numCols] = {9, 8, 7, 6, 5, 4, 3, 2}; //connect to the column pinouts of the keypad

//initialize an instance of class NewKeypad
/*Keypad customKeypad = Keypad( makeKeymap(Keys), rowPins, colPins, ROWS, COLS); 
*/
void setup()
{
  Serial.begin(9600);
  for (int row = 0; row < numRows; row++)
  {
    pinMode(rowPins[row],INPUT);       // Set row pins as input
    digitalWrite(rowPins[row],HIGH);   // turn on Pull-ups
  }
  for (int column = 0; column < numCols; column++)
  {
    pinMode(colPins[column],OUTPUT);     // Set column pins as outputs 
                                         // for writing
    digitalWrite(colPins[column],HIGH);  // Make all columns inactive
  }
}

void loop()
{
  char key = getKey();
  if( key != 0) {       // if the character is not 0 then 
                        // it's a valid key press
    /*Serial.print("Got key ");*/
    Serial.print(key);
  }
}

// returns with the key pressed, or 0 if no key is pressed
char getKey()
{
  char key = 0;                                  // 0 indicates no key pressed

  for(int column = 0; column < numCols; column++)
  {
    digitalWrite(colPins[column],LOW);         // Activate the current column.
    for(int row = 0; row < numRows; row++)     // Scan all rows for 
                                               // a key press.
    {
      if(digitalRead(rowPins[row]) == LOW)     // Is a key pressed?
      {
        delay(debounceTime);                   // debounce
        while(digitalRead(rowPins[row]) == LOW)
            ;                                  // wait for key to be released
        key = keymap[row][column];             // Remember which key 
                                               // was pressed.
      }
    }
    digitalWrite(colPins[column],HIGH);     // De-activate the current column.
  }
  return key;  // returns the key pressed or 0 if none
}
