// Общие функции для всех страниц Mini App

// Получаем объект Telegram WebApp, если он доступен
const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;

// Вызвать Telegram.WebApp.ready(), если есть
function initTelegram() {
    if (tg) {
        tg.ready();
    }
}

// Показать кнопку "Назад" и повесить обработчик
function setBackButton(onClick) {
    if (!tg) return;
    tg.BackButton.show();
    tg.BackButton.onClick(onClick);
}

// Скрыть кнопку "Назад"
function hideBackButton() {
    if (!tg) return;
    tg.BackButton.hide();
    tg.BackButton.onClick(function () {});
}

// Базовый URL API. Вариант: брать из window.location.origin
// Если nginx отдаёт и статику, и /api с одного домена, это самый простой вариант.
const API_BASE = window.location.origin;

// Получить параметр из URL (?id=...)
function getQueryParam(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
}

// Загрузить список разделов на главной странице
async function loadSections() {
    initTelegram();
    hideBackButton();

    const listContainer = document.getElementById("sections-list");
    const messageEl = document.getElementById("message");

    try {
        const resp = await fetch(API_BASE + "/api/sections");
        if (!resp.ok) {
            throw new Error("Ошибка ответа сервера");
        }
        const data = await resp.json();
        const sections = data.sections || [];

        if (!sections.length) {
            messageEl.textContent = "Разделов пока нет. Обратитесь к администратору.";
            return;
        }

        sections.forEach((section) => {
            const card = document.createElement("div");
            card.className = "card";

            const imgWrapper = document.createElement("div");
            imgWrapper.className = "card-image-wrapper";

            const img = document.createElement("img");
            img.className = "card-image";
            img.src = section.image_url || "";
            img.alt = section.title || "";
            if (!section.image_url) {
                img.style.display = "none";
            }

            imgWrapper.appendChild(img);
            card.appendChild(imgWrapper);

            const content = document.createElement("div");
            content.className = "card-content";

            const titleEl = document.createElement("div");
            titleEl.className = "card-title";
            titleEl.textContent = section.title;

            const descEl = document.createElement("div");
            descEl.className = "card-description";
            descEl.textContent = section.description || "";

            content.appendChild(titleEl);
            content.appendChild(descEl);
            card.appendChild(content);

            card.addEventListener("click", () => {
                // Переход на страницу раздела
                window.location.href = "section.html?id=" + encodeURIComponent(section.id);
            });

            listContainer.appendChild(card);
        });
    } catch (e) {
        console.error(e);
        messageEl.textContent = "Не удалось загрузить разделы. Попробуйте позже.";
    }
}

// Загрузить раздел и его подразделы
async function loadSectionPage() {
    initTelegram();

    const sectionId = getQueryParam("id");
    const titleEl = document.getElementById("section-title");
    const descEl = document.getElementById("section-description");
    const listContainer = document.getElementById("subsections-list");
    const messageEl = document.getElementById("message");

    if (!sectionId) {
        messageEl.textContent = "Не указан ID раздела.";
        return;
    }

    setBackButton(() => {
        window.location.href = "index.html";
    });

    try {
        const resp = await fetch(API_BASE + "/api/sections/" + encodeURIComponent(sectionId) + "/subsections");
        if (!resp.ok) {
            throw new Error("Ошибка ответа сервера");
        }
        const data = await resp.json();
        const section = data.section;
        const subsections = data.subsections || [];

        if (!section) {
            messageEl.textContent = "Раздел не найден.";
            return;
        }

        titleEl.textContent = section.title || "";
        descEl.textContent = section.description || "";

        if (!subsections.length) {
            messageEl.textContent = "Подразделов пока нет.";
            return;
        }

        subsections.forEach((sb) => {
            const card = document.createElement("div");
            card.className = "card";

            const imgWrapper = document.createElement("div");
            imgWrapper.className = "card-image-wrapper";

            const img = document.createElement("img");
            img.className = "card-image";
            img.src = sb.image_url || "";
            img.alt = sb.title || "";
            if (!sb.image_url) {
                img.style.display = "none";
            }

            imgWrapper.appendChild(img);
            card.appendChild(imgWrapper);

            const content = document.createElement("div");
            content.className = "card-content";

            const titleDiv = document.createElement("div");
            titleDiv.className = "card-title";
            titleDiv.textContent = sb.title;

            const descDiv = document.createElement("div");
            descDiv.className = "card-description";
            descDiv.textContent = sb.description || "";

            content.appendChild(titleDiv);
            content.appendChild(descDiv);
            card.appendChild(content);

            card.addEventListener("click", () => {
                // Переход на страницу подраздела
                const url = "subsection.html?id=" + encodeURIComponent(sb.id) +
                    "&section_id=" + encodeURIComponent(sectionId);
                window.location.href = url;
            });

            listContainer.appendChild(card);
        });
    } catch (e) {
        console.error(e);
        messageEl.textContent = "Не удалось загрузить данные. Попробуйте позже.";
    }
}

// Загрузить подраздел и его материалы
async function loadSubsectionPage() {
    initTelegram();

    const subsectionId = getQueryParam("id");
    const sectionId = getQueryParam("section_id");

    const titleEl = document.getElementById("subsection-title");
    const descEl = document.getElementById("subsection-description");
    const listContainer = document.getElementById("materials-list");
    const messageEl = document.getElementById("message");

    if (!subsectionId) {
        messageEl.textContent = "Не указан ID подраздела.";
        return;
    }

    setBackButton(() => {
        if (sectionId) {
            window.location.href = "section.html?id=" + encodeURIComponent(sectionId);
        } else {
            window.location.href = "index.html";
        }
    });

    try {
        const resp = await fetch(
            API_BASE + "/api/subsections/" + encodeURIComponent(subsectionId) + "/materials"
        );
        if (!resp.ok) {
            throw new Error("Ошибка ответа сервера");
        }
        const data = await resp.json();
        const subsection = data.subsection;
        const materials = data.materials || [];

        if (!subsection) {
            messageEl.textContent = "Подраздел не найден.";
            return;
        }

        titleEl.textContent = subsection.title || "";
        descEl.textContent = subsection.description || "";

        if (!materials.length) {
            messageEl.textContent = "Материалов пока нет.";
            return;
        }

        materials.forEach((m) => {
            const btn = document.createElement("button");
            btn.className = "material-button";

            const mainText = document.createElement("div");
            mainText.textContent = m.title;

            const subText = document.createElement("div");
            subText.style.fontSize = "12px";
            subText.style.color = "#555555";
            subText.textContent = m.description || "";

            btn.appendChild(mainText);
            btn.appendChild(subText);

            btn.addEventListener("click", () => {
                if (m.tg_link) {
                    window.open(m.tg_link, "_blank");
                } else {
                    alert("Для этого материала не указана ссылка.");
                }
            });

            listContainer.appendChild(btn);
        });
    } catch (e) {
        console.error(e);
        messageEl.textContent = "Не удалось загрузить данные. Попробуйте позже.";
    }
}