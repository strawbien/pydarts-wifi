#include <Keyboard.h>
#define NUM_ROWS 8
#define NUM_COLS 9
#define DEBOUNCE_VALUE 100
#define REPEAT_DELAY 500

// Keymap for normal use

byte keyMap[NUM_ROWS][NUM_COLS] = {
  {'0','1','2','4','5','6','7','8','9'},
  {'a','b','c','d','e','f','g','h','i'},
  {'j','k','l','m','n','o','p','q','r'},
  {'s','t','u','v','w','x','y','z','A'},
  {'B','C','D','E','F','G','H','I','J'},
  {'K','L','M','N','O','P','Q','R','S'},
  {'T','U','V','W','X','Y','Z','+','-'},
  {'*','/','?','!','&','$','@','#','_'}  
};
// Global Variables
int debounceCount[NUM_ROWS][NUM_COLS];
int altKeyFlag;
bool serial_output;

// Define the row and column pins

byte colPins[NUM_COLS] = {A0,A1,A2,A3,15,14,16,10,1}; // A,B,C,D,E,F,G,H
byte rowPins[NUM_ROWS] = {2,3,4,5,6,7,8,9};

// SETUP

void setup()
{
  // Set all pins as inputs and activate pull-ups
  serial_output = false;
  for (byte c = 0 ; c < NUM_COLS ; c++)
  {
    pinMode(colPins[c], INPUT);
    digitalWrite(colPins[c], HIGH);

    // Clear debounce counts

    for (byte r = 0 ; r < NUM_ROWS ; r++)
    {
      debounceCount[r][c] = 0;
    }
  }

  // Set all pins as inputs

  for (byte r = 0 ; r < NUM_ROWS ; r++)
  {
    pinMode(rowPins[r], INPUT);
  }

  // Function key is NOT pressed

  // Initialise the keyboard
  if (serial_output )
   {
    Serial.begin(9600);
   }
   else
   {
    Keyboard.begin();
   }
}

// LOOP

void loop()
{

  bool keyPressed = false;

    for (byte r = 0 ; r < NUM_ROWS ; r++)
    {
      // Run through the rows, turn them on

      pinMode(rowPins[r], OUTPUT);
      digitalWrite(rowPins[r], LOW);

      for (byte c = 0 ; c < NUM_COLS ; c++)
      {
        if (digitalRead(colPins[c]) == LOW)
        {
          // Increase the debounce count

          debounceCount[r][c]++;

          // Has the switch been pressed continually for long enough?

          int count = debounceCount[r][c];
          if (count == DEBOUNCE_VALUE)
          {
            // First press

            keyPressed = true;
            pressKey(r, c);
          }

          else if (count > DEBOUNCE_VALUE)
          {
            // Check for repeats

            count -= DEBOUNCE_VALUE;
            if (count % REPEAT_DELAY == 0)
            {
              // Send repeat

              keyPressed = true;
              pressKey(r, c );
            }
          }
        }
        else
        {
          // Not pressed; reset debounce count

          debounceCount[r][c] = 0;
        }
      }

    // Turn the row back off

    pinMode(rowPins[r], INPUT);
    }
}

void pressKey(byte r, byte c)
{
  // Send the keypress
  if (serial_output)
    {
    Serial.print("|");Serial.print("\r\n");Serial.print("|");
    Serial.print(r);Serial.print(",");Serial.print(c);Serial.print(":");
    }
  byte key = keyMap[r][c];

  if (serial_output)
   {
   if (key > 0){ Serial.write(key);}
   }
   else
   {
   if (key > 0 ) Keyboard.write(key);
   }

}
