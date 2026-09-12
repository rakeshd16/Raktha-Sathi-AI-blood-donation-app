// PWA Helper - Install Prompt Management
let deferredPrompt;
let installPromptShown = false;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event for later use
  deferredPrompt = e;
  // Show the install button/prompt
  showInstallPrompt();
});

function showInstallPrompt() {
  // Create a banner if it doesn't exist
  let installBanner = document.getElementById('pwa-install-banner');
  if (!installBanner) {
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.className = 'fixed bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 text-white p-4 flex items-center justify-between z-50 shadow-lg';
    banner.innerHTML = `
      <div class="flex items-center gap-3 flex-1">
        <i class="fas fa-download text-lg"></i>
        <div>
          <p class="font-semibold">Install Rakt-Sathi</p>
          <p class="text-sm opacity-90">Get quick access on your home screen</p>
        </div>
      </div>
      <div class="flex gap-2">
        <button onclick="installApp()" class="bg-white text-red-600 px-4 py-2 rounded font-semibold hover:bg-gray-100">
          Install
        </button>
        <button onclick="dismissInstallPrompt()" class="text-white px-3 py-2 hover:bg-red-800 rounded">
          ✕
        </button>
      </div>
    `;
    document.body.appendChild(banner);
  }
}

function installApp() {
  if (deferredPrompt) {
    // Show the install prompt
    deferredPrompt.prompt();
    // Wait for the user to respond to the prompt
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      deferredPrompt = null;
      dismissInstallPrompt();
    });
  }
}

function dismissInstallPrompt() {
  const banner = document.getElementById('pwa-install-banner');
  if (banner) {
    banner.remove();
  }
}

// Handle app installed event
window.addEventListener('appinstalled', () => {
  console.log('PWA was installed');
  deferredPrompt = null;
  dismissInstallPrompt();
});

// Check if running as PWA
function isPWA() {
  return window.navigator.standalone === true || 
         window.matchMedia('(display-mode: standalone)').matches;
}

// Enable share functionality for PWA
if (navigator.share) {
  window.shareData = function(title, text, url) {
    navigator.share({
      title: title,
      text: text,
      url: url || window.location.href
    }).catch(err => console.log('Error sharing:', err));
  };
}

console.log('PWA Helper loaded. PWA mode:', isPWA());
