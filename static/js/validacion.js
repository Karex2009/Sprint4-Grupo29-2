function validar_formulario() {
    var username = document.formRegistro.username;
    var email = document.formRegistro.email;
    var password = document.formRegistro.password;
  
    var username_len = username.value.length;
    if (username_len == 0 || username_len < 8) {
      alert("Debes ingresar un username con min. 8 caracteres");
      passid.focus();
      return false; //Para la parte dos, que los datos se conserven
    }
  
    var formato_email = /^\w+([\.-]?\w+)@\w+([\.-]?\w+)(\.\w{2,3})+$/;
    if (!email.value.match(formato_email)) {
      alert("Debes ingresar un email electronico valido!");
      email.focus();
      return false; //Para la parte dos, que los datos se conserven
    }
  
    var passid_ok = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,15}/;
    if (!password.value.match(passid_ok)) {
      alert("Minimo 8 caracteres maximo 1. Al menos una letra mayúscula y al menos una letra minuscula. Al menos un dígito No espacios en blanco. Al menos 1 caracter especial");
      passid.focus();
    }

    var pass_equals = document.formRegistro.getElementByName(passw)
  }
  
  function mostrarPassword(obj) {
    var obj = document.getElementById("password");
    obj.type = "text";
  }
  function ocultarPassword(obj) {
    var obj = document.getElementById("password");
    obj.type = "password";
  }
  
  function showForm() {
    document.getElementById("formRegistro").style.display = "block";
  }
  
  function hideForm() {
    document.getElementById("formRegistro").style.display = "none";
  }
  