

function addComment(input) {
    // Get Comment Info
    let comment_input_text = document.getElementById(input)
    let commentValue = comment_input_text.value


    // Clear Comment Input
    comment_input_text.value = ""

    // Call Jquery AJAX
    $.ajax({
        url: "/socialnetwork/add-comment",
        type: "POST",
        data: `comment_text=${commentValue}&post_id=${input}&csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType: "json",
        success: updateGlobalPost,
        error: errorGlobalPost
    });

}

/** Sends AJAX Call to Get All instances of Global Post Objects */
function loadGlobalPost() {
    $.ajax({
        url: "/socialnetwork/get-global",
        dataType: "json",
        success: updateGlobalPost,
        error: errorGlobalPost
    });

}

/** Sends AJAX Call to Get All instances of Follower Post Objects */
function loadFollowerPost() {
    $.ajax({
        url: "/socialnetwork/get-follower",
        dataType: "json",
        success: updateGlobalPost,
        error: errorGlobalPost
    });

}



/** Updates Comments and Posts on Global and Follower Pages */
function updateGlobalPost(post_dic) {

    let post_div;
    if (post_dic["page"] === "global") {
        post_div = document.getElementById("id_global_content_div");
    } else if (post_dic["page"] === "follower") {
        post_div = document.getElementById("id_follower_content_div");
    }

    post_dic["posts"].forEach(post => {
        //Create a div for each Post in Json
        if (document.getElementById(`id_post_comment_group_${post.id}`) == null) {
            // Load Post
            post_div.prepend(createPostItem(post));
            // Load comment section layout
            document.getElementById(`id_post_comment_group_${post.id}`).append(addCommentSection(post.id))
        }

    })

    let comment_div;
    let comment_input;
    post_dic["comments"].forEach(comment => {

        if (document.getElementById(`id_comment_div_${comment.id}`) == null) {
            // Add Comment to existing comment section
            comment_div = document.getElementById(`id_comment_section_${comment.post_id}`)
            comment_input = document.getElementById(`id_comment_list_item_${comment.post_id}`)

            comment_div.prepend(createComment(comment))

        }
    })
}

function updateFollowerPost(post_dic) {
    let follower_post_div = document.getElementById("id_follower_content_div");

    post_dic["posts"].forEach(post => {
        //Create a div for each Post in Json
        if (document.getElementById(`id_post_comment_group_${post.id}`) == null) {
            // Load Post
            follower_post_div.prepend(createPostItem(post));
            // Load comment section layout
            document.getElementById(`id_post_comment_group_${post.id}`).append(addCommentSection(post.id))
        }

    })

    let comment_div;
    let comment_input;
    post_dic["comments"].forEach(comment => {

        if (document.getElementById(`id_comment_div_${comment.id}`) == null) {
            // Add Comment to existing comment section
            comment_div = document.getElementById(`id_comment_section_${comment.post_id}`)
            comment_input = document.getElementById(`id_comment_list_item_${comment.post_id}`)

            comment_div.prepend(createComment(comment))

        }
    })
}


function createPostItem(post) {
    let id_string = String(post.id)

    /** Create Outer div */
    let post_div = document.createElement("div");
    post_div.className = "row justify-content-center align-items-center bg-secondary py-2";
    post_div.id = "id_post_comment_group_" + id_string

    /** Create Card Div */
    let card_div = document.createElement("div");
    card_div.className = "card post-group"
    card_div.id = "id_post_div_" + id_string;

    /** Create Card Body */
    let card_body = document.createElement("div");
    card_body.className = "card-body";
    // Post Profile Link
    profile_link = document.createElement("a");
    profile_link.id = "id_post_profile_" + id_string
    profile_link.className = "card-text post-profile-link "
    profile_link.href = "/socialnetwork/other-profile/" + post.profile_id
    profile_link.innerHTML = `Post by ${sanitize(post.first_name)} ${sanitize(post.last_name)}`
    profile_span = document.createElement("span");
    profile_span.appendChild(profile_link)
    // Post Text
    post_text = document.createElement("span")
    post_text.id = "id_post_text_" + id_string
    post_text.className = "card-text post-text px-4"
    post_text.innerHTML = `${sanitize(post.post_input_text)}`
    // Append Content
    card_body.appendChild(profile_span)
    card_body.appendChild(post_text)


    /** Create Card Footer */
    let card_footer = document.createElement("div")
    card_footer.className = "card-footer"
    // Append Date / Time
    let date_span = document.createElement("span")
    date_span.id = "id_post_date_time_" + id_string
    date_span.className = "text-muted post-date-time"
    date_span.innerHTML = `${sanitize(post.date_time)}`
    // Append Content
    card_footer.appendChild(date_span)


    // Append DOM items
    card_div.appendChild(card_body)
    card_div.appendChild(card_footer)
    post_div.appendChild(card_div)
    return post_div

}

// Create Comment Section for each post
function addCommentSection(post_id) {
    /** Set up Outer Divs */
    let comment_section_div = document.createElement("div")
    comment_section_div.id = "id_comment_section_" + post_id
    comment_section_div.className = "card"
    let comment_list = document.createElement("ul")
    comment_list.className = "list-group list-group-light"
    comment_section_div.appendChild(comment_list)

    /** Add Comment Input */
    comment_section_div.appendChild(createCommentInput(post_id))

    return comment_section_div
}

// Create individual comment
function createComment(comment) {
    /** Create Outer Divs */
    let comment_list_item = document.createElement("li")
    comment_list_item.className = "list-group-item"
    let comment_group_div = document.createElement("div")
    comment_group_div.id = "id_comment_div_" + String(comment.id)
    comment_group_div.className = "container-fluid comment-group"
    let comment_row_1 = document.createElement("div")
    comment_row_1.className = "row d-flex flex-row"
    let comment_row_2 = document.createElement("div")
    comment_row_2.className = "row d-flex flex-row"
    //Append to DOM
    comment_group_div.appendChild(comment_row_1)
    comment_group_div.appendChild(comment_row_2)
    comment_list_item.appendChild(comment_group_div)

    /** Create input content*/
    // Post Profile Link
    profile_link = document.createElement("a");
    profile_link.id = "id_comment_profile_" + String(comment.id)
    profile_link.className = "text comment-profile-link"
    profile_link.href = "/socialnetwork/other-profile/" + comment.profile_id
    profile_link.innerHTML = `Comment by ${sanitize(comment.first_name)} ${sanitize(comment.last_name)}`
    profile_span = document.createElement("span");
    profile_span.appendChild(profile_link)
    // Post Text
    post_text = document.createElement("span")
    post_text.id = "id_comment_text_" + String(comment.id)
    post_text.className = "text comment-text px-4"
    post_text.innerHTML = `${sanitize(comment.comment_input_text)}`
    // Append to DOM
    comment_row_1.appendChild(profile_span)
    comment_row_1.appendChild(post_text)

    /** Create Date time row */
    let date_span = document.createElement("span")
    date_span.id = "id_comment_date_time_" + String(comment.id)
    date_span.className = "text-muted comment-date-time"
    date_span.innerHTML = `${sanitize(comment.date_time)}`
    // Append to DOM
    comment_row_2.appendChild(date_span)

    return comment_list_item

}

// Create Comment Input 
function createCommentInput(post_id) {
    /** Create Outer Divs */
    let comment_list_item = document.createElement("li")
    comment_list_item.className = "list-group-item"
    comment_list_item.id = "id_comment_list_item_" + post_id
    let comment_list_container = document.createElement("div")
    comment_list_container.className = "container-fluid"
    let comment_list_row = document.createElement("div")
    comment_list_row.className = "row flex-row"
    let comment_list_input_group = document.createElement("div")
    comment_list_input_group.className = "input-group new-comment-group"
    // Append All to DOM
    comment_list_row.appendChild(comment_list_input_group)
    comment_list_container.appendChild(comment_list_row)
    comment_list_item.appendChild(comment_list_container)

    /** Create Input Content */
    let comment_input_text = document.createElement("input")
    comment_input_text.type = "text"
    comment_input_text.id = "id_comment_input_text_" + post_id
    comment_input_text.className = "form-control new-comment-text"
    let comment_input_label = document.createElement("label")
    comment_input_label.className = "input-group-text new-comment-label"
    comment_input_label.htmlFor = comment_input_text.id
    comment_input_label.innerHTML = "New Comment:"
    let comment_input_button = document.createElement("button")
    comment_input_button.id = "id_comment_button_" + post_id
    comment_input_button.className = "btn btn-light new-comment-button"
    comment_input_button.onclick = function () { addComment(comment_input_text.id) };
    comment_input_button.innerHTML = "Submit"
    // Append to DOM
    comment_list_input_group.appendChild(comment_input_label)
    comment_list_input_group.appendChild(comment_input_text)
    comment_list_input_group.appendChild(comment_input_button)

    return comment_list_item
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}


function errorGlobalPost(xhr) {
    if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText)
        updateGlobalPost(response)
        return
    }

    if (xhr.status === 0) {
        alert("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        alert("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        alert(response.error)
        return
    }

    alert(response)
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}