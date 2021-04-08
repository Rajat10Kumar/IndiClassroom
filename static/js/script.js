$("form[name=signup_form").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();
  var radioValue = $("input[name='isTeacher']:checked").val();
  console.log("hello" + data + radioValue);
  $.ajax({
    url: "/user/signup",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      console.log("A");
      console.log(radioValue + "Hello");
      if (!radioValue) {
        window.location.href = "/dashboard/";
        myFunction(resp["isTeacher"]);
      } else {
        window.location.href = "/classroom/";
        myFunction(resp["isTeacher"]);
      }

      console.log(radioValue + "Hello");
      console.log("B");
    },
    error: function (resp) {
      console.log("C");
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
      console.log("D");
    },
  });

  e.preventDefault();
});
$("form[name=login_form").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();
  // var radioValue = $("input[name='isTeacher']:checked").val();
  $.ajax({
    url: "/user/login",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      // console.log(data + "Hello");
      // console.log(radioValue + "Hello");
      // console.log(resp['isTeacher']);
      if (resp["isTeacher"]) {
        window.location.href = "/classroom/";
        myFunction(resp["isTeacher"]);
      } else {
        window.location.href = "/dashboard/";
        myFunction(resp["isTeacher"]);
      }
    },
    error: function (resp) {
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    },
  });

  e.preventDefault();
});
function myFunction(isTeacher) {
  var x = document.getElementById("myDIV");
  if (isTeacher) {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}

$("form[name=make_class").submit(function (e) {
  // console.log("ddgd");
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();
  console.log(data);
  // var radioValue = $("input[name='isTeacher']:checked").val();
  $.ajax({
    url: "/classroom/create",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      // e.preventDefault();
      console.log("a");
      console.log(resp);
      // window.location.reload();
    },
    error: function (resp) {
      console.log("b");
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    },
  });
  e.preventDefault();
  return false;
});
$("form[name=join_class").submit(function (e) {
  // console.log("ddgd");
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();
  console.log(data);
  // var radioValue = $("input[name='isTeacher']:checked").val();
  $.ajax({
    url: "/dashboard/join",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      e.preventDefault();
      console.log("a");
      console.log(resp);
    },
    error: function (resp) {
      console.log("b");
      $error.text(resp.responseJSON.error).removeClass("error--hidden");
    },
  });
});
$("form[name=assignment").submit(function (e) {
  var cid = document.getElementsByName("cid");
  window.location("/enter/" + cid);
});
