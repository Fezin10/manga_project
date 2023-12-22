document.addEventListener("DOMContentLoaded", () => {
    // Retain an user or manga to analysis
    if (document.querySelector("#analysis_button")) {
        let analysis = document.querySelector("#analysis_button");
        let url = analysis.getAttribute("data-url");
        analysis.removeAttribute("data-url");
        analysis.addEventListener("click", () => {
            let check = window.prompt("Report the problem: ");
            if (check !== null) {
                fetch(`${url}?reason=${check}`)
                    .then((response) => response.json())
                    .then((data) => {
                        if (data["status"] === "success") {
                            location.reload();
                        } else {
                            alert("Fail");
                        }
                    });
            }
        });
    }

    // Let the user register themself as an author
    if (document.querySelector("#author_button")) {
        let author_button = document.querySelector("#author_button");
        let url = author_button.getAttribute("data-url");
        author_button.removeAttribute("data-url");
        author_button.addEventListener("click", () => {
            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    if (data["status"] == "success") {
                        location.reload();
                    } else {
                        alert("Fail");
                    }
                });
        });
    }

    // Count how much caracters the user have left in their manga sinopse
    if (document.querySelector("#counter")) {
        let counter = document.querySelector("#counter");
        let sinopse = document.querySelector("#sinopse");
        counter.innerText = 300 - sinopse.value.length + " characters left.";
        sinopse.addEventListener("input", () => {
            counter.innerText = 300 - sinopse.value.length + " characters left.";
        });
    }

    // Darkmode
    {
        theme = localStorage.getItem("theme");
        if (theme === null) {
            localStorage.setItem("theme", "light");
            theme = "light";
        }
        let darkmode = document.querySelector("#darkmode");
        if (theme === "dark" || theme === "auto") {
            document.documentElement.setAttribute("data-bs-theme", "dark");
            darkmode.innerText = "Light";
        } else {
            document.documentElement.removeAttribute("data-bs-theme");
            darkmode.innerText = "Dark";
        }
        darkmode.addEventListener("click", () => {
            if (theme === "dark" || theme === "auto") {
                theme = "light";
                document.documentElement.removeAttribute("data-bs-theme");
                darkmode.innerText = "Dark";
                localStorage.setItem("theme", theme);
            } else {
                theme = "dark";
                document.documentElement.setAttribute("data-bs-theme", "dark");
                darkmode.innerText = "Light";
                localStorage.setItem("theme", theme);
            }
        });
    }

    // Delete the manga of the page you are if you're the author of the manga
    if (document.querySelector("#delete_button")) {
        let button = document.querySelector("#delete_button");
        button.addEventListener("click", (event) => {
            let confirmation = confirm("Are you sure you want to delete?");
            if (!confirmation) {
                event.preventDefault();
            }
        });
    }

    // Keep the dropdown menu open when clicking in the label
    if (document.querySelector("#filter_dropdown")) {
        function stop(element) {
            element.querySelectorAll("li").forEach((e) => {
                e.addEventListener("click", (event) => {
                    event.stopPropagation();
                });
            });
        }

        stop(document.querySelector("#filter_dropdown"));
        stop(document.querySelector("#genre_dropdown"));
    }

    // Follow button for the userpage
    if (document.querySelector("#follow_button")) {
        let follow_button = document.querySelector("#follow_button");
        let url = follow_button.getAttribute("data-url");
        follow_button.removeAttribute("data-url");
        follow_button.addEventListener("click", () => {
            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    if (data["status"] !== "success") {
                        alert("Fail when trying to un/follow the user");
                    } else {
                        if (data["following"] == true) {
                            follow_button.innerText = "Unfollow";
                        } else {
                            follow_button.innerText = "Follow";
                        }
                        document.querySelector("#followers").innerText = `Followers: ${data["following_count"]}`;
                    }
                });
        });
    }

    // Free or block some user or manga
    if (document.querySelector("#free_button")) {
        let free = document.querySelector("#free_button");
        let ban = document.querySelector("#block_button");

        function call(event) {
            let url = event.currentTarget.getAttribute("data-url");
            let check = document.querySelector("#fault");
            let ban_author = document.querySelector("#ban_author");
            if (check.checked) {
                url += "?fault=True";
                if (ban_author && ban_author.checked) {
                    url += "&ban=True";
                }
            } else if (ban_author && ban_author.checked) {
                url += "?ban=True";
            }
            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    if (data["status"] === "success") {
                        window.location.href = "../../";
                    } else {
                        alert("Operation failed!");
                    }
                });
        }
        ban.addEventListener("click", call);
        free.addEventListener("click", call);
    }

    // Function to create a preview for the image files sended in some pages
    if (document.querySelector("#image_preview")) {
        let preview = document.querySelector("#image_preview");

        function preview_image(event) {
            let input = event.target;
            preview.innerHTML = "";
            if (input.files && input.files.length > 0) {
                let promises = [];
                // Loop to get each image and put then inside a bootstrap grid structure
                for (let i = 0; i < input.files.length; i++) {
                    let promise = new Promise((resolve) => {
                        let col = document.createElement("div");
                        col.className = "col-3";
                        let figure = document.createElement("figure");
                        figure.className = "figure";
                        let figcaption = document.createElement("figcaption");
                        figcaption.className = "figure-caption";
                        figcaption.innerText = `${String(i + 1).padStart(3, "0")} image.`;

                        let reader = new FileReader();
                        reader.onload = function (e) {
                            let image = document.createElement("img");
                            image.src = e.target.result;
                            image.alt = `${i + 1} image preview`;
                            image.className = "figure-img img-fluid";
                            figure.appendChild(image);
                            figure.appendChild(figcaption);
                            col.appendChild(figure);
                            resolve(col);
                        };
                        reader.readAsDataURL(input.files[i]);
                    });

                    promises.push(promise);
                }

                // Make the images show in the order the user selected
                Promise.all(promises).then((columns) => {
                    let row;
                    columns.forEach((col, index) => {
                        if (index % 3 === 0) {
                            if (row) {
                                preview.appendChild(row);
                            }
                            row = document.createElement("div");
                            row.className = "row";
                        }
                        row.appendChild(col);
                    });
                    if (row) {
                        preview.appendChild(row);
                    }
                });
            }
        }
        document.querySelector("#image_input").addEventListener("change", preview_image);
    }

    // Like button for the mangapage
    if (document.querySelector("#like_button")) {
        let like_button = document.querySelector("#like_button");
        let url = like_button.getAttribute("data-url");
        like_button.removeAttribute("data-url");
        like_button.addEventListener("click", () => {
            fetch(url)
                .then((response) => response.json())
                .then((data) => {
                    if (data["status"] !== "success") {
                        alert("Can not complete the like process");
                    } else {
                        if (data["liked"] === true) {
                            like_button.innerText = "❤️";
                        } else {
                            like_button.innerText = "🤍";
                        }
                        document.querySelector("#likes").innerText = `Likes: ${data["likes"]}`;
                    }
                });
        });
    }

    // Show each image at a time in the page visualization page
    if (document.querySelector("#page_view")) {
        let visualization = document.querySelector("#view").innerHTML;
        document.querySelector("#view").remove();
        let index = 0; // keeps track of which image to show
        let pages = document.querySelectorAll(".page_read");

        // all images besides the first are being hidden
        for (let i = 1; i < pages.length; i++) {
            pages[i].style.display = "none";
        }

        let next = document.querySelector("#next");
        next.style.display = "none";
        let previous = document.querySelector("#previous");
        previous.style.display = "none";

        // handle the clicks to change the image
        document.querySelector("#next_button").addEventListener("click", left);
        document.querySelector("#previous_button").addEventListener("click", right);
        // handles when the navbar is being used
        document.querySelector("#navbar-toggler").addEventListener("click", () => {
            setTimeout(changetop, 320);
        });

        document.addEventListener("keydown", handleArrowKey);

        // Go to next image
        function left() {
            // if in the far right, hides it, and show the first image
            if (previous.style.display == "inline") {
                pages[index].style.display = "inline";
                previous.style.display = "none";
            } else {
                pages[index].style.display = "none";
                if (index + 1 >= pages.length) {
                    next.style.display = "inline";
                    // mark the chapter as read if reach the last next chapter page
                    fetch(visualization);
                    // update the touch area if in the mobile version
                    changetop();
                } else {
                    index++;
                    pages[index].style.display = "inline";
                }
            }
        }

        // Go to previous image
        function right() {
            // if in the far left, render the last image and hide the next chapter button
            if (next.style.display == "inline") {
                next.style.display = "none";
                pages[index].style.display = "inline";
            } else {
                pages[index].style.display = "none";
                if (index - 1 < 0) {
                    previous.style.display = "inline";
                    changetop();
                } else {
                    index--;
                    pages[index].style.display = "inline";
                }
            }
        }

        // update the size of the touch area to change page
        function changetop() {
            let n = document.querySelector("#next_button");
            let p = document.querySelector("#previous_button");
            let value;
            if (previous.style.display !== "none") {
                // update the touch area to let the user click the link
                value = previous.offsetTop + parseFloat(window.getComputedStyle(previous).fontSize) * 2 + "px";
            } else if (next.style.display !== "none") {
                value = next.offsetTop + parseFloat(window.getComputedStyle(next).fontSize) * 2 + "px";
            } else {
                value = pages[index].offsetTop + "px";
            }

            n.style.top = value;
            p.style.top = value;
        }

        // go to next or previous page if the user presses right or left key
        function handleArrowKey(event) {
            if (event.key == "ArrowLeft") {
                left();
            } else if (event.key == "ArrowRight") {
                right();
            }
        }

        changetop();
    }

    // build the pc mangapage if not mobile device
    if (!isMobileDevice()) {
        try {
            document.getElementById("page_image").className = "col";
            document.getElementById("page_content").className = "col";
        } catch {
            null;
        }
    }

    // VALIDATIONS

    // addchapter page
    if (document.querySelector("#addchapter_form")) {
        let form = document.querySelector("#addchapter_form");
        let message = document.querySelector("#message");
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            message.innerText = "";
            let error = false;
            let chapter = document.querySelector("#chapter").value;
            if (!Number.isInteger(parseInt(chapter)) || chapter < 1 || chapter > 32767) {
                message.innerText += " Invalid chapter value!";
                error = true;
            }
            let images = document.querySelector("#image_input").files;
            for (let i = 0; i < images.length; i++) {
                if (!isImage(images[i])) {
                    message.innerText += " Invalid files given as images!";
                    error = true;
                    break;
                }
            }
            if (!error) {
                form.submit();
            }
        });
    }

    // addmanga page
    if (document.querySelector("#addmanga_form")) {
        let form = document.querySelector("#addmanga_form");
        let message = document.querySelector("#message");
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            message.innerText = "";
            let error = false;

            let manga_name = document.querySelector("#manga_name").value;
            if (manga_name.length > 50 || manga_name.length < 1) {
                error = true;
                message.innerText += " Invalid manga name!";
            }
            let status = document.querySelector("#status").value;
            if (status !== "F" && status !== "R" && status !== "N") {
                error = true;
                message.innerText += " Invalid status!";
            }
            let sinopse = document.querySelector("#sinopse").value;
            if (sinopse.length > 300) {
                error = true;
                message.innerText += " Sinopse is too long!";
            }
            let releasedate = document.querySelector("#releasedate").value;
            if (releasedate && !isValidDate(releasedate)) {
                error = true;
                message.innerText += " Invalid release date!";
            }
            let enddate = document.querySelector("#enddate").value;
            if (enddate && !isValidDate(enddate)) {
                error = true;
                message.innerText += " Invalid end date!";
            }
            let image = document.querySelector("#image_input").files[0];
            if (image && !isImage(image)) {
                error = true;
                message.innerText += " Invalid file given as image!";
            }

            if (!error) {
                form.submit();
            }
        });
    }

    // edituser page
    if (document.querySelector("#edituser_form")) {
        let form = document.querySelector("#edituser_form");
        let message = document.querySelector("#message");
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            message.innerText = "";
            let error = false;

            let username = form.querySelector("#username").value;
            if (username.length < 1) {
                error = true;
                message.innerText += "Invalid username";
            }

            let password = form.querySelector("#password").value;
            if (password && password.length < 4) {
                error = true;
                message.innerText += " Password is too short!";
            }
            let confirmation = form.querySelector("#confirmation").value;
            if (password && !confirmation) {
                error = true;
                message.innerText += " You need to provide a password and confirm it";
            }
            if (password && confirmation && password !== confirmation) {
                error = true;
                message.innerText += " The password and the confirmation must match!";
            }
            let image = form.querySelector("#image_input").files[0];
            if (image && !isImage(image)) {
                error = true;
                message.innerText += " Invalid file given as icon";
            }

            if (!error) {
                form.submit();
            }
        });
    }

    // register page
    if (document.querySelector("#register_form")) {
        let form = document.querySelector("#register_form");
        let message = document.querySelector("#message");
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            message.innerText = "";
            let error = false;

            let username = form.querySelector("#username").value;
            if (username.length < 1) {
                error = true;
                message.innerText += "Invalid username";
            }

            let email = form.querySelector("#email").value;
            if (!isValidEmail(email)) {
                error = true;
                message.innerText += " Invalid email!";
            }

            let password = form.querySelector("#password").value;
            let confirmation = form.querySelector("#confirmation").value;
            if (!password || !confirmation) {
                error = true;
                message.innerText += " You need to provide a password and confirm it";
            } else if (password.length < 4) {
                error = true;
                message.innerText += " Password is too short!";
            } else if (password !== confirmation) {
                error = true;
                message.innerText += " The password and the confirmation must match!";
            }

            let image = form.querySelector("#image_input").files[0];
            if (image && !isImage(image)) {
                error = true;
                message.innerText += " Invalid file given as icon";
            }

            if (!error) {
                form.submit();
            }
        });
    }
});

function isImage(file) {
    return file.type.startsWith("image/");
}

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isValidDate(dateString) {
    const parsedDate = new Date(dateString);
    return !isNaN(parsedDate.getTime()) && dateString === parsedDate.toISOString().split("T")[0];
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
