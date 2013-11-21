#include <iostream>
#include <fstream>

using namespace std;

int pointsPerByteCorrect = 6; // gives remainder of 4 points for 4 questions, so give those for free

extern char *yourName;
extern char *studentID;
//extern int numTests; //we want to always do 4 tests

extern void bit_operations(unsigned long inputDWord, unsigned long *outputDWord);
//use this declaration for compiling without linking to student submission
//void bit_operations(unsigned long inputDWord, unsigned long *outputDWord) {*outputDWord = 0x55aa033c;}

int main(int args, char ** argv)
{
  char* ucinetid = "NO_UCINETID";
  if (args > 1) {
    ucinetid = argv[1];
  }

  int numTests = 4;
  unsigned long myVar;
  unsigned long tmpValue;
  unsigned long shouldBe;
  int i, totalCorrect=4; //100 isn't evenly divisible by 4 tests that are each 4 bytes, so just give them the remainder
  
  // Test Generator (up to four)
  if( numTests > 4 )
    numTests = 4;

  // Expected values
  for( i = 0; i < numTests; i++){
    switch( i ){
    case 0: myVar = 0xaa00a1f2;
      shouldBe = 0x55aa033c;
      break;
    case 1: myVar = 0x0c0c0c0c;
      shouldBe = 0x30a602c3;
      break;
    case 2: myVar = 0xa0b0c0d0;
      shouldBe = 0x051a023c;
      break;
    case 3: myVar = 0x80ff85f0;
      shouldBe = 0x0155033c;
      break;
    default: myVar = 0xaa00a1f2;
      shouldBe = 0x55aa033c;
    }

    //printf("RUNNING TEST %d :: ", i+1);
    //printf("INPUT BYTES: %X\n\n", myVar);

    tmpValue = myVar;

    bit_operations(myVar, &tmpValue);
    //printf("RESULT -> SHOULD BE: %X - is: %X\n\n", shouldBe, tmpValue);

    // score results, giving partial credit for getting individual bytes correct
    if ((tmpValue & 0x000000ff) == (shouldBe & 0x000000ff))
      totalCorrect += pointsPerByteCorrect;
    if ((tmpValue & 0x0000ff00) == (shouldBe & 0x0000ff00))
      totalCorrect += pointsPerByteCorrect;
    if ((tmpValue & 0x00ff0000) == (shouldBe & 0x00ff0000))
      totalCorrect += pointsPerByteCorrect;
    if ((tmpValue & 0xff000000) == (shouldBe & 0xff000000))
      totalCorrect += pointsPerByteCorrect;
  }

  // Output total correct to file named as ucinetid
  ofstream out_file;
  out_file.open(ucinetid);
  out_file << ucinetid << "," << totalCorrect << endl;
  out_file.close();

  return 0;
}
