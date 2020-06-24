function submitForm() {
  var frm = document.getElementsByName('searchform')[0];
  frm.submit(); // Submit the form
  frm.reset(); // Reset all form data
  return false; // Prevent page refresh
}
//athletestats
function visibleonclick1() {
  document.querySelector('#runs').style.display = "initial";
}
  function visibleonclick2() {
    document.querySelector('#swims').style.display = "initial";
  }
  function visibleonclick() {
    document.querySelector('#rides').style.display = "initial";
  }
  function visibleonclick3() {
    document.querySelector('#stats').style.display = "initial";
  }
  $(".custom-file-input").on("change", function() {
  var fileName = $(this).val().split("\\").pop();
  $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});

  var slideIndex = 1;
  showSlides(slideIndex);

  function plusSlides(n) {
    showSlides(slideIndex += n);
  }

  function currentSlide(n) {
    showSlides(slideIndex = n);
  }

  function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    if (n > slides.length) {
      slideIndex = 1
    }
    if (n < 1) {
      slideIndex = slides.length
    }
    for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }
    slides[slideIndex - 1].style.display = "block";
  }

  function imagevisibleonclick() {
    document.querySelector('#imageslideshow').style.display = "initial";
  }

  function imagevisibleonclick1() {
    document.querySelector('#deleteimages').style.display = "initial";
  }

  function clubvisibleonclick() {
    document.querySelector('#clubmembers').style.display = "initial";
  }

  function clubvisibleonclick1() {
    document.querySelector('#clubdata').style.display = "initial";
  }
