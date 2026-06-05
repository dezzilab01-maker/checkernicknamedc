const { Client, GatewayIntentBits } = require('discord.js-selfbot-v13');
const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

const DISCORD_TOKEN = 'TWÓJ_TOKEN_DISCORDA';
const GUILD_ID = '1489241760264618186';
const CHANNEL_ID = '1492577129056043202';
const DISCORD_LOGIN_URL = 'https://discord.com/login';

let driver;

async function initBrowser() {
    const options = new chrome.Options();
    options.addArguments('--start-maximized', '--no-sandbox', '--disable-dev-shm-usage');
    driver = await new Builder().forBrowser('chrome').setChromeOptions(options).build();
    console.log('[Browser] Przeglądarka uruchomiona.');
}

async function openUrl(url) {
    const handles = await driver.getAllWindowHandles();
    if (handles.length === 1 && (await driver.getCurrentUrl()) === 'about:blank') {
        await driver.get(url);
    } else {
        await driver.executeScript(`window.open('${url}', '_blank');`);
        const newHandles = await driver.getAllWindowHandles();
        await driver.switchTo().window(newHandles[newHandles.length - 1]);
    }
    console.log(`[Browser] Otwarto: ${url}`);
}

async function loginDiscord(email, password) {
    await driver.get(DISCORD_LOGIN_URL);
    try {
        const wait = new (require('selenium-webdriver').WebDriverWait)(driver, 20000);
        const emailField = await wait.until(until.elementLocated(By.name('email')));
        await emailField.clear();
        await emailField.sendKeys(email);

        const passwordField = await driver.findElement(By.name('password'));
        await passwordField.clear();
        await passwordField.sendKeys(password);

        const loginButton = await driver.findElement(By.xpath("//button[@type='submit']"));
        await loginButton.click();
        console.log(`[Browser] Próba logowania na Discord jako ${email}`);
    } catch (e) {
        console.log(`[Browser] Błąd logowania: ${e}`);
    }
}

function extractUrls(text) {
    const regex = /https?:\/\/[^\s<>"\'\[\]]+/g;
    return text.match(regex) || [];
}

function extractCredentials(text) {
    const regex = /[\w.+-]+@[\w-]+\.[\w.-]+:[^\s,;]+/g;
    return text.match(regex) || [];
}

const client = new Client({
    intents: [
        GatewayIntentBits.GUILDS,
        GatewayIntentBits.GUILD_MESSAGES,
        GatewayIntentBits.MESSAGE_CONTENT
    ]
});

client.on('ready', async () => {
    console.log(`[Bot] Zalogowano jako ${client.user.tag} (ID: ${client.user.id})`);
    console.log(`[Bot] Monitoruję kanał ${CHANNEL_ID} na serwerze ${GUILD_ID}`);
    await initBrowser();
});

client.on('messageCreate', (message) => {
    if (message.author.id === client.user.id) return;
    if (message.channel.id !== CHANNEL_ID) return;

    const content = message.content;
    console.log(`[Bot] Nowa wiadomość od ${message.author.tag}: ${content.substring(0, 80)}...`);

    const urls = extractUrls(content);
    urls.forEach(url => {
        console.log(`[Bot] Znaleziono link: ${url}`);
        openUrl(url);
    });

    const credentials = extractCredentials(content);
    credentials.forEach(cred => {
        const [email, password] = cred.split(':');
        console.log(`[Bot] Znaleziono dane logowania: ${email}:${password.substring(0, 3)}***`);
        loginDiscord(email, password);
    });
});

client.on('disconnect', async () => {
    if (driver) await driver.quit();
    console.log('[Bot] Zasoby wyczyszczone.');
});

client.login(DISCORD_TOKEN);
