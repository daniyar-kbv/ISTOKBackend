django.jQuery( document ).ready(function() {
    console.log( "ready!" );
    django.jQuery('#client_profile-group').css("display", "none");

    django.jQuery('#id_role').change(function() {
      alert( "Handler for #id_role was called." );
    });
});