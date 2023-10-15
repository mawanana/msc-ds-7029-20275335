

def get_unique_elements(data_array):
    print("calling done operator")
    # Create a new list to store the unique elements
    unique_elements = []
    # Iterate through the array
    for element in data_array:
        # If the element is not already in the list, add it
        if element not in unique_elements:
            unique_elements.append(element)
    return unique_elements


