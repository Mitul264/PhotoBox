var screenWidth = (window.screen.width * window.devicePixelRatio) * 0.98;
var screenHeight = (window.screen.length * window.devicePixelRatio) * 0.98;

var userName = "";
var sessionId = "";
var upToDateImages = null;
var upToDateLinks = {};


$(document).ready(function ()
{
  initializeModal();
  checkCookie();
  $(".initialHide").hide();
  $(".uploadSect").hide();
  $("#home").show();
  listeners();
  set();

});

function set()
{
  getUpdatedPhotos();
  // Keep running getMessages frequently to update the front end
  setInterval(getUpdatedPhotos, 3000);
}

function getUpdatedPhotos()
{
  checkCookie();
  var linkRequest = "/~patelm5/cgi-bin/serve.cgi?user=" + userName+"&session=" + sessionId+"&newTab=No";
  if(upToDateImages == null)
  {
    linkRequest = "/~patelm5/cgi-bin/serve.cgi?user=" + userName+"&session=" + sessionId+"&newTab=Yes";
  }

  var xmlHttpReq = new XMLHttpRequest();
  xmlHttpReq.open("GET", linkRequest, true);
  xmlHttpReq.setRequestHeader("Content-Type","text/plain");
  xmlHttpReq.onreadystatechange = function()
  {   //Call a function when the state changes.
    if(xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
    {
      var response = xmlHttpReq.responseText;
      if(response != "ERROR")
      {
        var myResponseObj = JSON.parse(response);
        if(myResponseObj != null)
        {
          if(myResponseObj["info"] != "LogInPlease")
          {
            if(myResponseObj["info"] == "changed")
            {
              upToDateImages = myResponseObj["photos"];
              upToDateLinks =  myResponseObj["links"];

              var lenDict = Object.keys(upToDateImages).length;
              updatePhotos(upToDateImages);
              updateUsageQuota(lenDict);
            }
            // else, we have the most up to date data

          }
          else {
            showModal("Failed to fetch resources, please log in first!",1);
            window.location.replace("/~patelm5/cgi-bin/identifier.cgi");
          }
        }
        else
        {
          getUpdatedPhotos();
        }
      }
      else
      {
        getUpdatedPhotos();
      }
    }else if (xmlHttpReq.readyState == 4)
    {
      getUpdatedPhotos();
    }

  }
  xmlHttpReq.send();
}


function copySharableLink(theImage)
{
    showModalTwo(document.getElementById("link"+theImage).value);
}

function deleteImage(theImage)
{
    var relayDict = {};
    relayDict["command"] = "delete";
    relayDict["user"] = userName;
    relayDict["session"] = sessionId;
    relayDict["photo"] = theImage;
    var sendStr = JSON.stringify(relayDict);

    var xmlHttpReq = new XMLHttpRequest();
    xmlHttpReq.open("POST", "/~patelm5/cgi-bin/serve.cgi", true);
    xmlHttpReq.setRequestHeader("Content-Type","text/plain");
    xmlHttpReq.onreadystatechange = function()
    {   //Call a function when the state changes.
      if(xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
      {
        var response = xmlHttpReq.responseText;
        if(response != "ERROR")
        {
          var imageDeleted = JSON.parse(response);
          if(imageDeleted["info"] == "Yes")
          {
            showModal("Photo Deleted!",1);
            getUpdatedPhotos();
            showOuter("home");
          }
          else
          {
            showModal("Unable to delete photo, could have already been deleted",1);
          }

        }
        else
        {
          showModal("An error occured while deleting the photo from the cloud",1);
        }
      }
    }
    xmlHttpReq.send(sendStr);
}


function imageClick(theId)
{

  $(".initialHide").hide();
  $(".hideImage").hide();
  document.getElementById(theId).style.display = "block";
  closeNav();
}

function emailImageShow(theId)
{
  document.getElementById("emailLink"+theId).style.display = "block";
  document.getElementById("emailLinkButton"+theId).style.display = "block";
}

function emailImageSend(theId)
{
  var relayDict = {};
  relayDict["command"] = "email";
  relayDict["user"] = userName;
  relayDict["email"] = document.getElementById("emailLink"+theId).value;
  relayDict["photo"] = theId;
  var sendStr = JSON.stringify(relayDict);

  var xmlHttpReq = new XMLHttpRequest();
  xmlHttpReq.open("POST", "/~patelm5/cgi-bin/email.cgi", true);
  xmlHttpReq.setRequestHeader("Content-Type","text/plain");
  xmlHttpReq.onreadystatechange = function()
  {   //Call a function when the state changes.
    if(xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
    {
      var response = xmlHttpReq.responseText;
      if(response != "ERROR")
      {
        var imageDeleted = JSON.parse(response);
        if(imageDeleted["info"] == "Yes")
        {
          showModal("Email Sent Successfully!",1);
          document.getElementById("emailLink"+theId).style.display = "none";
          document.getElementById("emailLinkButton"+theId).style.display = "none";

        }
        else
        {
          showModal("An error occured while sending the email!",1);
        }

      }
      else
      {
        showModal("An error occured while sending the email!",1);
      }
    }
    else if (xmlHttpReq.readyState == 4)
    {
      showModal("An error occured while sending the email!",1);
    }
  }
  xmlHttpReq.send(sendStr);
}

function updatePhotos(images)
{
  var mySidenav = "<a href='javascript:void(0)' class='closebtn' onclick='closeNav()'>&times;</a>";
  var mainStr = "";

  for (var key in images)
  {
    if (images.hasOwnProperty(key))
    {
        mySidenav+="<a onclick='imageClick(\"" + key + "\")' href='#'>" + key + "</a>";
        mainStr+= "<div id='" + key + "' class='hideImage'><button type='button' style='margin: 20px;background-color: red;color: white' class='btn btn-outline-dark' onclick=\"deleteImage(\'" + key + "\')\">Delete</button><button type='button' style='margin: 20px;background-color: #00990d;color: white' class='btn btn-outline-dark' onclick=\"copySharableLink(\'" + key + "\')\">Generate Sharable Link</button><button type='button' style='margin: 20px;background-color: blue;color: white' class='btn btn-outline-dark' onclick=\"emailImageShow(\'" + key + "\')\">Email Photo</button><input disabled style='width: 750px;color: white; background-color: #00990d;' type='text' class='hideImage' value='"+upToDateLinks[key]+"' id='link" + key + "'><input placeholder='Enter Email Address' style='width: 500px;color: black; background-color: white;' type='text' class='hideImage' id='emailLink" + key + "'><button id='emailLinkButton" + key + "' type='button' style='margin: 10px;background-color: black;color: white' class='btn btn-outline-dark hideImage' onclick=\"emailImageSend(\'" + key + "\')\">Send</button><br><img style='border: 8px solid; padding: 8px;' id='dvPreview" + key + "' src='" +images[key] + "'>	</img></div>";

    }
  }
  document.getElementById("mySidenav").innerHTML = mySidenav
  document.getElementById("main").innerHTML = mainStr
  $(".hideImage").hide();
}

function updateUsageQuota(freeSpace)
{
  var totalSpace = 10;

  document.getElementById('freeSpace').innerHTML = "Free Space (BLACK): " + (totalSpace - freeSpace);
  document.getElementById('usedSpace').innerHTML = "Used Space (PURPLE):" + + freeSpace;

  var freeDegrees = Math.floor((freeSpace/totalSpace) * 360);
  var theChart = document.getElementById('myPieChart');
  theChart.style.backgroundImage = "conic-gradient(#c978ff "+freeDegrees+"deg,#222 0 360deg)";
}


function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0, and the background color of body to white */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  document.body.style.backgroundColor = "white";
}

function showOuter(showItem)
{
  $(".initialHide").hide();
  $(".hideImage").hide();
  $("#"+showItem).show();

}

function addImage(theImage, theImageName)
{
  var relayDict = {};
  relayDict["command"] = "add";
  relayDict["user"] = userName;
  relayDict["session"] = sessionId;
  relayDict["photo"] = theImageName;
  relayDict["photodata"] = theImage;
  var sendStr = JSON.stringify(relayDict);
  // XHR request
  var xmlHttpReq = new XMLHttpRequest();
  xmlHttpReq.open("POST", "/~patelm5/cgi-bin/serve.cgi", true);
  xmlHttpReq.setRequestHeader("Content-Type","text/plain");
  xmlHttpReq.onreadystatechange = function()
  {   //Call a function when the state changes.
    if(xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
    {
      var response = xmlHttpReq.responseText;
      if(response != "ERROR")
      {
        var imageAdded = JSON.parse(response);
        if(imageAdded != null && "info" in imageAdded)
        {
          if(imageAdded["info"] == "Yes")
          {
            showModal("Photo Added to Cloud!",1);
            $("#theImageDisplay").hide();
            document.getElementById("fileLablel").innerText = "No File Selected";
            document.getElementById("uploadFile").value = "";

          }
          else if(imageAdded["info"] == "Duplicate")
          {
            showModal("Unable to Add photo, image with the same name exists in Cloud!",1);
            $("#theImageDisplay").hide();
            document.getElementById("fileLablel").innerText = "No File Selected";
            document.getElementById("uploadFile").value = "";
          }
          else if(imageAdded["info"] == "Full")
          {
            showModal("Unable to Add photo, Quota full!",1);
            clearUploadContents();
          }
        }
        else
        {
          showModal("An Error occured while uploading the image!",1);
          clearUploadContents();
        }

      }
      else {
        showModal("An Error occured while uploading the image!",1);
        clearUploadContents();
      }
    }
    else if(xmlHttpReq.readyState == 4)
    {
      showModal("An Error occured while uploading the image!",1);
    }
  }
  xmlHttpReq.send(sendStr);
}

function clearUploadContents()
{
  $("#theImageDisplay").hide();
  document.getElementById("fileLablel").innerText = "No File Selected";
  document.getElementById("uploadFile").value = "";
}

function initializeModal()
{
  document.getElementById("modalDiv").innerHTML = "<div class='modal fade' id='myModal' tabindex='-1' role='dialog' aria-labelledby='displayModal' aria-hidden='true'> <div class='modal-dialog modal-dialog-centered' role='document'> <div class='modal-content'> <div class='modal-body'> <h2 id='modalParagraph'></h2> </div> </div> </div> </div><div class='modal fade' id='myModalTwo' tabindex='-1' role='dialog' aria-labelledby='displayModal' aria-hidden='true'> <div class='modal-dialog modal-lg' role='document'> <div class='modal-content'> <div class='modal-body'> <h5 id='modalParagraphTwo'></h5> </div> </div> </div> </div>";
}

function showModalTwo(message)
{
  document.getElementById("modalParagraphTwo").innerText = message;
  $("#myModalTwo").modal();
}


function showModal(message, theInt)
{
  document.getElementById("modalParagraph").innerText = message;
  $("#myModal").modal();
}

function uploadImage()
{
  var thevalue = document.getElementById("uploadFile");
  if (thevalue != "")
  {
    var finalVal = thevalue.value.split("\\");
    var len = finalVal.length;
    var newStr = finalVal[len - 1];
    newStr = newStr.split(".");
    if(newStr[1] == "png" || newStr[1] == "jpg" || newStr[1] == "jpeg")
    {
      if (typeof (FileReader) != "undefined") {
        var reader = new FileReader();
        reader.onload = function (e) {
            var base64File = reader.result;
            addImage(base64File, finalVal[len - 1]);
        }
        reader.readAsDataURL(thevalue.files[0]);
      } else
      {
          showModal("This browser does not support FileReader.",1);
      }
    }
    else
    {
      showModal("Please Upload a png/jpg/jpeg",1);
    }
  }
  else
  {
    $("#theImageDisplay").hide();
  }
}

function listeners()
{
  $("#uploadFile").change(function ()
  {
    var label = document.getElementById("fileLablel");
    var thevalue = document.getElementById("uploadFile");
    if (thevalue != "")
    {
      var finalVal = thevalue.value.split("\\");
      var len = finalVal.length;
      var newStr = finalVal[len - 1];
      newStr = newStr.split(".");

      if(newStr[1] == "png" ||newStr[1] == "PNG" || newStr[1] == "jpg" || newStr[1] == "jpeg")
      {
        label.innerText = finalVal[len - 1];
        if (typeof (FileReader) != "undefined") {
          var reader = new FileReader();
          $("#theImageDisplay").css("overflow-x", "scroll");
          $("#theImageDisplay").css("margin", "20px");
          $("#theImageDisplay").css("height", screenHeight+"px");
          $("#theImageDisplay").css("max-width", screenWidth+"px");

          reader.onload = function (e) {
              $("#dvPreview").attr("src", e.target.result);
          }
          reader.readAsDataURL(thevalue.files[0]);
          $("#theImageDisplay").show();

        } else
        {
            showModal("This browser does not support FileReader.",1);
        }
      }
      else
      {
        showModal("Please Upload a png/jpg/jpeg",1);
      }

    }
    else
    {
      $("#theImageDisplay").hide();
    }

  });
}


// Get cookie funtions from https://www.w3schools.com/js/js_cookies.asp
function checkCookie() {
  var username = getCookie("guestid");
  var session = getCookie("sessionid");
  userName = username;
  sessionId = session;
  if (userName != "" && sessionId != "")
  {
    var sendDict = {};
    sendDict["command"] = "verify";
    sendDict["user"] = userName;
    sendDict["session"] = sessionId;
    var sendStr = JSON.stringify(sendDict);
    // XHR request
    var xmlHttpReq = new XMLHttpRequest();
    xmlHttpReq.open("POST", "/~patelm5/cgi-bin/serve.cgi", true);
    xmlHttpReq.setRequestHeader("Content-Type","text/plain");
    xmlHttpReq.onreadystatechange = function()
    {   //Call a function when the state changes.
      if(xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
      {
        var response = xmlHttpReq.responseText;
        if(response != "ERROR")
        {
          var myResponseObj = JSON.parse(response);
          if((myResponseObj == null) ||(myResponseObj != null && "existance" in myResponseObj && myResponseObj["existance"] == 0))
          {
            showModal("You must log in first",1);
            window.location.replace("/~patelm5/cgi-bin/identifier.cgi");
          }
        }
      }
      else if(xmlHttpReq.readyState == 4)
      {
        showModal("You must log in first",1);
        window.location.replace("/~patelm5/cgi-bin/identifier.cgi");
      }
    }
    xmlHttpReq.send(sendStr);
  }
  else
  {
    showModal("You must log in first",1);
    window.location.replace("/~patelm5/cgi-bin/identifier.cgi");
  }
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
