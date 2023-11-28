function validateFile() {
    var inputFile = document.getElementById('image');
    var fileSize = inputFile.files[0].size; // in bytes
    var fileType = inputFile.files[0].type;

    // File size check (in bytes, here limiting to 5 MB)
    if (fileSize > 2097152) {
      alert('File size exceeds 5 MB. Please choose a smaller file.');
      return false;
    }

    // File type check (you can adjust this based on your requirements)
    if (!fileType.startsWith('image/')) {
      alert('Invalid file type. Please choose an image file.');
      return false;
    }

    return true; // Proceed with form submission
}