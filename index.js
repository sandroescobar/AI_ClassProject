
/****************************************************
 * 1. LOAD EXISTING CATEGORIES ON PAGE LOAD
 ****************************************************/

/*


let categories = []; // Global category array

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded. Loading categories from localStorage...");

    // Retrieve 'categories' from localStorage
    const storedCategories = JSON.parse(localStorage.getItem('categories')) || [];
    categories = storedCategories; // Update global array

    
   

    // Populate the dropdown
    populateDropdown(categories);

    

});



/**
 * Populates the select dropdown with a list of categories.
 * @param {Array} catList - Array of category strings
 */

/** 
function populateDropdown(catList) {
    const categorySelect = document.querySelector('.categorySelect');
    if (!categorySelect) {
        console.log("Dropdown element not found.");
        return;
    }

    // Clear existing options except for the first placeholder
    categorySelect.innerHTML = '<option value="" disabled selected>Select a category</option>';

    // Add each category as an <option>
    catList.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });
}

/****************************************************
 * 2. SHOW/HIDE MODAL FOR ADDING NEW CATEGORIES
 ****************************************************/


/*
const addCategoryButton = document.querySelector('.add-category');
console.log("Add Category button found: ", addCategoryButton);

if (addCategoryButton){

    addCategoryButton.addEventListener('click', () => {
        const modal = document.querySelector('.modal');
        console.log("Modal element found: ", modal);
        modal.style.display = 'flex';
    });

}
else{
    console.log("Add Category button not found.");
}




const closeModalButton = document.querySelector('.cancelCategory');
console.log("Cancel button found: ", closeModalButton);

if (closeModalButton){
    closeModalButton.addEventListener('click', () => {
        const modal = document.querySelector('.modal');
        modal.style.display = 'none';
    });
}
else{
    console.log("Cancel button not found.");
}


/****************************************************
 * 3. ADD NEW CATEGORY (SUBMIT) & SAVE TO LOCALSTORAGE
 ****************************************************/

/*

submitCategoryButton = document.querySelector('.submitCategory');

if (submitCategoryButton){
    submitCategoryButton.addEventListener('click', (event) => {
        event.preventDefault(); // Stop the browser from submitting the form automatically
    
        const modal = document.querySelector('.modal');
        const inputElement = document.querySelector('.categoryName');
        const form = inputElement.closest('form'); // Grabs the form the input is inside
    
        const inputCategory = inputElement.value.trim();
    
        if (inputCategory === "") {
            alert("Category name cannot be empty!");
            return; // Don't continue if input is empty
        }
    
        console.log("Category name: ", inputCategory);
    
        // Update dropdown and localStorage before submission
        if (!categories.includes(inputCategory)) {
            categories.push(inputCategory);
            localStorage.setItem('categories', JSON.stringify(categories));
            populateDropdown(categories);
        }
    
        form.submit();
    
        // Hide modal and clear input AFTER saving, BEFORE submission
        modal.style.display = 'none';
    
        // ✅ Don't clear the input just yet – let the backend see it
        // inputElement.value = ''; // Only clear after form submits successfully
    
        // ✅ Submit form manually (this includes the input value now)
        
    });
    
    
}else{
    console.log("Submit button not found.");
}



document.addEventListener("DOMContentLoaded", () => {
    const uploadFileImg = document.querySelector('.upload-file');
    console.log("Upload file button found: ", uploadFileImg);

    uploadFileImg.addEventListener('click', () => {
        const hiddenInput = document.querySelector('.file-upload_input');
        hiddenInput.click(); // Directly trigger the file dialog
    });
});





// Select the parent element (body.InventoryPageBody)


/****************************************************
 * 4. HELPER EXPLANATION
 ****************************************************/
/*
 - On page load, we run `document.addEventListener('DOMContentLoaded', ...)`
   which loads existing categories from localStorage into the global `categories` array,
   then calls `populateDropdown(categories)` to display them.

 - When a user adds a new category:
   1) We push it into the `categories` array.
   2) We save that array back to localStorage (so it's persisted).
   3) We call `populateDropdown(categories)` to update the UI immediately.

 This way, the user sees the new category right away, 
 and if they refresh the page, localStorage ensures the categories remain.
*/


/****************************************************
 * 1. LOAD EXISTING CATEGORIES ON PAGE LOAD VIA FETCH
 ****************************************************/
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded. Fetching categories from backend...");

    // Fetch categories from the backend getCategories endpoint
    fetchCategories();

    // Attach event listener for file upload button
    const uploadFileImg = document.querySelector('.upload-file');
    if(uploadFileImg) {
        console.log("Upload file button found:", uploadFileImg);
        uploadFileImg.addEventListener('click', () => {
            const hiddenInput = document.querySelector('.file-upload_input');
            if (hiddenInput) {
                hiddenInput.click(); // Trigger the file dialog
            } else {
                console.log("File upload input not found.");
            }
        });
    } else {
        console.log("Upload file button not found.");
    }
});

/**
 * Fetch categories from the backend and populate the dropdown.
 */
function fetchCategories() {
    fetch('/getCategories')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched categories:", data);
            // Populate the dropdown with the fetched categories.
            populateDropdown(data);
            // Optionally, save the latest categories to localStorage:
            localStorage.setItem('categories', JSON.stringify(data));
        })
        .catch(error => {
            console.error("Error fetching categories:", error);
            // Fallback: try to load from localStorage if available.
            const storedCategories = JSON.parse(localStorage.getItem('categories')) || [];
            populateDropdown(storedCategories);
        });
}

/**
 * Populates the select dropdown with a list of categories.
 * @param {Array} catList - Array of category strings
 */
function populateDropdown(catList) {
    const categorySelect = document.querySelector('.categorySelect');
    if (!categorySelect) {
        console.log("Dropdown element not found.");
        return;
    }
    // Clear existing options, add a default placeholder
    categorySelect.innerHTML = '<option value="" disabled selected>Select a category</option>';
    catList.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });
}

/****************************************************
 * 2. SHOW/HIDE MODAL FOR ADDING NEW CATEGORIES
 ****************************************************/
const addCategoryButton = document.querySelector('.add-category');
console.log("Add Category button found:", addCategoryButton);
if (addCategoryButton) {
    addCategoryButton.addEventListener('click', () => {
        const modal = document.querySelector('.modal');
        if (modal) {
            console.log("Modal element found:", modal);
            modal.style.display = 'flex';
        } else {
            console.log("Modal element not found.");
        }
    });
} else {
    console.log("Add Category button not found.");
}

const closeModalButton = document.querySelector('.cancelCategory');
console.log("Cancel button found:", closeModalButton);
if (closeModalButton) {
    closeModalButton.addEventListener('click', () => {
        const modal = document.querySelector('.modal');
        if (modal) {
            modal.style.display = 'none';
        }
    });
} else {
    console.log("Cancel button not found.");
}

/****************************************************
 * 3. ADD NEW CATEGORY (SUBMIT) & UPDATE LOCAL DATA
 ****************************************************/
const submitCategoryButton = document.querySelector('.submitCategory');
if (submitCategoryButton) {
    submitCategoryButton.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent the default form submission

        const modal = document.querySelector('.modal');
        const inputElement = document.querySelector('.categoryName');
        const form = inputElement.closest('form'); // Grab the form that the input is inside

        const inputCategory = inputElement.value.trim();
        if (inputCategory === "") {
            alert("Category name cannot be empty!");
            return; // Stop if input is empty.
        }

        console.log("Category name to add:", inputCategory);

        // (Optional) Update localStorage and dropdown immediately
        let storedCategories = JSON.parse(localStorage.getItem('categories')) || [];
        if (!storedCategories.includes(inputCategory)) {
            storedCategories.push(inputCategory);
            localStorage.setItem('categories', JSON.stringify(storedCategories));
            populateDropdown(storedCategories);
        }

        // Submit the form to add the category via backend
        form.submit();

        // Hide modal after submission
        modal.style.display = 'none';
    });
} else {
    console.log("Submit button not found.");
}






    







