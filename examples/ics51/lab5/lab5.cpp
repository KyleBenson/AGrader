/*
----- LAB5 ------

Motivation:
Practise more with function; learn to operate simple data structre, such as Linked List

ASSIGNMENT:

(1) Write the first function

list* process_list(list* list_beg, list* new_element)

that gets as parameters a pointer to a linked list (list_beg) and a pointer to a linked 
list element (new_element). The function should go through the list, find and delete the 
elements with the maximum value (if there are several such elements, all of them should 
be deleted from the list), and then call insert_element to insert the new_element into 
list_beg. Please refer to (2).

NOTE: You can assume that the first element is never the maximum element so that you will 
not be required to delete it. The size of the list is 0 or 2 or more elements.

(2) Write the second function

list* insert_element(list* list_beg, list* new_element)

You need to pass two parameters to the function: list_beg and new_element. Insert right after 
the first element with the value 0 if found, otherwise don't insert. The function should
return the pointer to the list element with the value 0 or, if not found, return NULL. Note 
that the list can be empty, but the new_element can never be NULL.

Insertion means that the element with the value 0 should point to the new element and the new 
element should point to the element that was after the element with 0 value in the initial list.

Example:
If list_beg is pointing to a list with values {3, -5, 5, 3, 0, 2} and new_element is pointing 
to an element with value 7, after calling the function the list should look like 
{3, -5, 3, 0, 7, 2} and the function should return a pointer to the element with value 0.

Please note that
1)'return NULL' means return EAX with its value as 0; 'the new_element can never be NULL' means
the address of pointer '*new_element' is never 0

2)the function is declared as not using epilog and prolog code, so you need to fetch
function parameters directly from stack (without using parameter variables), implement proper
return from the function and save/restore all the registers the function uses.
*/

#include <stdio.h>

char *yourName = "Your Name";
char *studentID = "Student ID";

typedef struct linked_list {
  struct linked_list *next_element;	 // the pointer to the next element in the list
  int value;                         // the value of the element
} list;

list* insert_element(list* list_beg, list* new_element);

__declspec(naked) list* process_list(list* list_beg, list* new_element)
{
	__asm {
		// START CODING HERE

		// END CODING HERE
		ret
	}
}

__declspec(naked) list* insert_element(list* list_beg, list* new_element)
{
	__asm {
		// START CODING HERE

		// END CODING HERE
		ret
	}
}
