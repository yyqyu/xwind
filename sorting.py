# function calling
def sorting():

    # Declaring the hash function
    dictionary = {}

    # Initialize value
    dictionary[1000] = "VFR ADV FREQ 134.15MHZ U/S USE 125.15MHZ"
    dictionary[1] = 2
    dictionary[5] = 12
    dictionary[4] = 24
    dictionary[9] = 18
    dictionary[9] = 323

    print ("Task 2:-\nKeys and Values sorted in",
            "alphabetical order by the key  ")

    # sorted(dictionary) returns an iterator over the
    # Dictionary’s value sorted in keys.
    for i in sorted (dictionary, reverse=True) :
        print ((dictionary[i]), end =" ")

def main():
    # function calling
    sorting()

# main function calling
if __name__=="__main__":
    main()