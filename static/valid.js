function validate()
{
    var username=document.getElementById("username").value;
    var username=document.getElementById("password").value;
    if(username)
    if(username=="1999999" && password== "Admin12@")
    {
        alert("Login Successful");
        return false;
    }
    else if (username=="1999999" && password!== "Admin12@")
    {
        alert("Login Failed Incorrect Password");
        return true;
    }
    else 
    {
        alert("Record not Found. PLease Sign Up first")
        return true;
    }


}