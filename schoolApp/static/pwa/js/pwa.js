
let installPrompt = null;

document.addEventListener("DOMContentLoaded", () => {
  // Registar o Service Worker.
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/service-worker.js")
      .catch((error) => {
        console.error("Erro ao registar a PWA:", error);
      });
  }

  // Criar botão de instalação.
  const installButton = document.createElement("button");

  installButton.type = "button";
  installButton.textContent = "Instalar aplicação";
  installButton.hidden = true;

  installButton.style.cssText = `
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 9999;
    padding: 12px 18px;
    border: 0;
    border-radius: 10px;
    background: #123b6d;
    color: white;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 14px #0002;
  `;

  document.body.appendChild(installButton);

  // O navegador decide quando a instalação está disponível.
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    installButton.hidden = false;
  });

  installButton.addEventListener("click", async () => {
    if (!installPrompt) {
      return;
    }

    installPrompt.prompt();

    const choice = await installPrompt.userChoice;

    if (choice.outcome === "accepted") {
      installButton.hidden = true;
    }

    installPrompt = null;
  });

  window.addEventListener("appinstalled", () => {
    installButton.hidden = true;
    installPrompt = null;
  });

  // O evento de instalação não é suportado em todos os navegadores.
  // Nesses casos, o utilizador poderá instalar pelo menu do navegador.
});
