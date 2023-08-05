const open_menu = () => {
      
    document.getElementById("mobile-menu-icon").classList.add("hidden");
    document.getElementById("cancel-icon").classList.remove("hidden");
    document.getElementById("mobile-nav-bar").classList.remove("hidden");

  };
  const close_menu = () => {
    
    document.getElementById("mobile-menu-icon").classList.remove("hidden");
    document.getElementById("cancel-icon").classList.add("hidden");
    document.getElementById("mobile-nav-bar").classList.add("hidden");

  };