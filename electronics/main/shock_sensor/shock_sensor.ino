// int Shock = 10; // define the vibration sensor interface
int shockVal; // define numeric variables val
int shockIn;

bool readShock(shockIn){
    val = digitalRead (shockIn) ; // read digital interface is assigned a value of 3 val
    if (val == HIGH) // When the shock sensor detects a signal, LED flashes
    {
      return true;
    }
    else
    {
      return false;
    }
}

// Load below code to run standalone shock sensor test
//
// void setup ()
// {
//   pinMode (Led, OUTPUT) ; // define LED as output interface
//   pinMode (Shock, INPUT) ; // output interface defines vibration sensor
// }
// void loop ()
// {
//   val = digitalRead (Shock) ; // read digital interface is assigned a value of 3 val
//   if (val == HIGH) // When the shock sensor detects a signal, LED flashes
//   {
//     digitalWrite (Led, LOW);
//   }
//   else
//   {
//     digitalWrite (Led, HIGH);
//   }
// }
