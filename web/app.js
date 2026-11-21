const search = document.querySelector("#search");
const inventory = document.querySelector("#inventory");
const inventoryStatus = document.querySelector("#inventory-status");
const fields = ["symbol", "contract_account", "precision", "maximum_supply", "on_chain_status", "notes"];

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error);
  }
  return result;
}

async function showInventory() {
  try {
    const tokens = await fetchJson("/api/inventory");
    function render() {
      const query = search.value.trim().toLowerCase();
      const matches = tokens.filter(token =>
        [token.symbol, token.contract_account].some(value => value?.toLowerCase().includes(query))
      );
      const rows = matches.map(token => {
        const row = document.createElement("tr");
        for (const field of fields) {
          const cell = row.insertCell();
          cell.textContent = token[field] ?? "—";
        }
        return row;
      });
      inventory.replaceChildren(...rows);
      inventoryStatus.textContent = matches.length ? `${matches.length} of ${tokens.length} tokens` : "No matching tokens.";
    }
    search.addEventListener("input", render);
    render();
  } catch (error) {
    inventoryStatus.textContent = error.message;
  }
}

const form = document.querySelector("#factory-form");
const submit = form.querySelector("button");
const planStatus = document.querySelector("#plan-status");
const plan = document.querySelector("#plan");
const inventoryReview = document.querySelector("#inventory-review");
const downloadPlan = document.querySelector("#download-plan");

form.addEventListener("submit", async event => {
  event.preventDefault();
  const config = Object.fromEntries(new FormData(form));
  config.precision = Number(config.precision);
  config.chain = "proton-test";
  config.issuer = config.contract_account;
  submit.disabled = true;
  plan.hidden = true;
  inventoryReview.hidden = true;
  downloadPlan.hidden = true;
  if (downloadPlan.hasAttribute("href")) {
    URL.revokeObjectURL(downloadPlan.href);
    downloadPlan.removeAttribute("href");
  }
  planStatus.textContent = "Generating review plan…";
  try {
    const result = await fetchJson("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    const matchCount = result.inventory_matches.length;
    inventoryReview.textContent = matchCount
      ? `Warehouse records with symbol ${config.symbol}: ${matchCount}. Verify the chain, contract and issuer before creating or issuing.`
      : "No matching symbol in the warehouse. Check XPR testnet to confirm token availability.";
    inventoryReview.hidden = false;
    plan.textContent = result.plan;
    const reviewText = `# ${inventoryReview.textContent}\n${result.plan}\n`;
    downloadPlan.href = URL.createObjectURL(new Blob([reviewText], { type: "text/plain" }));
    downloadPlan.hidden = false;
    plan.hidden = false;
    planStatus.textContent = "Review plan generated.";
  } catch (error) {
    planStatus.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

showInventory();

const walletButton = document.querySelector("#connect-wallet");
const walletStatus = document.querySelector("#wallet-status");
const walletRpc = "https://rpc.api.testnet.metalx.com";
const xprTestnetId = "71ee83bcf52142d61019d95f9cc5427ba6a0d7ff8accd9e2088ae2abeaf3d3dd";
const appAccount = "tokenfactory";
let walletSdk;

function loadWalletSdk() {
  if (!walletSdk) {
    walletSdk = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://unpkg.com/@proton/web-sdk@5.1.0/lib/proton-web-sdk.bundle.js";
      script.integrity = "sha384-5XX6/myWSFmrVjyfcVWcXOvXilMksXwCPBMcdsk3/u0MmWE4fIF3iW+l/5MJsAl/";
      script.crossOrigin = "anonymous";
      script.onload = resolve;
      script.onerror = () => {
        script.remove();
        walletSdk = undefined;
        reject(new Error("The WebAuth SDK could not be loaded."));
      };
      document.head.append(script);
    });
  }
  return walletSdk;
}

walletButton.addEventListener("click", async () => {
  walletButton.disabled = true;
  walletStatus.textContent = "Open WebAuth and approve the XPR Testnet account connection.";
  try {
    await loadWalletSdk();
    const { session, link } = await window.ProtonWebSDK({
      linkOptions: {
        endpoints: [walletRpc],
        chainId: xprTestnetId,
        restoreSession: false,
        storagePrefix: "token-factory-xpr-testnet",
      },
      transportOptions: { requestAccount: appAccount },
      selectorOptions: { walletType: "webauth", enabledWalletTypes: ["webauth"] },
    });
    if (!session || !link) {
      throw new Error("WebAuth did not return a wallet session.");
    }
    const actor = String(session.auth.actor);
    const chainId = String(session.chainId);
    await link.removeSession(appAccount, session.auth, session.chainId);
    if (chainId !== xprTestnetId || !/^[a-z1-5.]{1,12}$/.test(actor)) {
      throw new Error("WebAuth did not confirm an XPR Testnet account.");
    }
    walletStatus.textContent = `Verified wallet account: ${actor} on XPR Testnet.`;
  } catch (error) {
    walletStatus.textContent = error.message || "WebAuth connection did not complete.";
  } finally {
    walletButton.disabled = false;
  }
});
