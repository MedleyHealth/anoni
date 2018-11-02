let form = $('#textform');
let textarea = $('.textarea-form')[0];
let originalDiv = $('#original')[0];
let scrubbedDiv = $('#scrubbed')[0];

form.submit(postScrub);


function postScrub(e) {

  e.preventDefault()

  let request = {
    contentType: 'application/json',
    text: textarea.value
  }

  let data = JSON.stringify(request)

  $.ajax({
      type: "POST",
      url: "/api/scrub",
      beforeSend: function(request) {
        request.setRequestHeader("Content-Type", 'application/json');
      },
      data: data,
      dataType: 'json',
      success: function (response) {
        let text = response['text']
        let scrubbed = response['scrubbed']

        originalDiv.innerText = text;
        scrubbedDiv.innerText = scrubbed;
      }
  })
}
