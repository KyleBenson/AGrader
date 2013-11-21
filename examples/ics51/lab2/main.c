#include <fstream>
#include <iostream>

extern char* name;
extern char* studentID;
extern int countLowerCaseCharacter(char *inputString);
// just so it compiles
//int countLowerCaseCharacter(char *inputString){ return 0; }

using namespace std;

int main(int args, char ** argv)
{
  char* ucinetid = "NO_UCINETID";
  if (args > 1) {
    ucinetid = argv[1];
  }

  int count, totalCorrect = 0;

  //printf("Name: %s\n", name);
  //printf("StudentID: %s\n\n", studentID);

  //test cases
  char* string1 = NULL;
  char* string2 = "QWERTY";
  char* string3 = "AAZZFF2134a94z271ZAF";
  char* string4 = "ZAzdDF2134a94z271ZrA";

  int exp1 = 0, exp2 = 0, exp3 = 2, exp4 = 5;

  //Test 1
  count = countLowerCaseCharacter(string1);

  if (count == exp1)
    totalCorrect++;
  //printf("%d\n", count);
  
  //Test 2
  count = countLowerCaseCharacter(string2);
  if (count == exp2)
    totalCorrect++;
   
  //Test 3
  count = countLowerCaseCharacter(string3);
  if (count == exp3)
    totalCorrect++;
 
  //Test 4
  count = countLowerCaseCharacter(string4);
  if (count == exp4)
    totalCorrect++;

  // Output total correct to file named as ucinetid
  ofstream out_file;
  out_file.open(ucinetid);
  out_file << ucinetid << "," << totalCorrect * 25 << endl;
  out_file.close();

  return 0;
}
