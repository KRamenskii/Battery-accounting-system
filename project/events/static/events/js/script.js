const FIELD_TRANSLATIONS = {
    // Общие поля
    'id': 'ID',
    'title': 'Название',
    'name': 'Имя',
    'description': 'Описание',
    'created_at': 'Дата создания',
    'updated_at': 'Дата обновления',
    'user': 'Пользователь',

    //BatteryType
    'manufacturer': 'Производитель',
    'battery_type_title': 'Модель',
    'nominal_voltage': 'Номинальное напряжение, В',
    'elements_count': 'Количество элементов в АБ',
    'lifespan': 'Срок службы, лет',
    'nominal_capacity_20': 'Номинальная ёмкость при 20-ти часовом разряде',
    'nominal_capacity_10': 'Номинальная ёмкость при 10-ти часовом разряде',
    'nominal_capacity_5': 'Номинальная ёмкость при 5-ти часовом разряде',
    'self_discharge': 'Саморазряд, %',
    'internal_resistance': 'Внутреннее сопротивление, мОм',
    'weight': 'Вес АБ, кг',

    //InstallationLocation
    'location_title': 'Название места установки',
    'location_type': 'Тип места установки',
    'system_title': 'Описание',
    'system_name': 'Название системы',
    'nominal_capacity': 'Номинальная емкость АБ, А⋅ч',
    'battery_count': 'Количество АБ',
    'parent_location': 'Родительское место',
    'nesting_level': 'Уровень вложенности',

    //SerialParameters
    'battery_type': 'Тип АБ',
    'serial_number': 'Серийный номер',
    'manufacture_date': 'Дата изготовления',

    //Battery
    'battery_type': 'Тип АБ',
    'serial_parameters': 'Серийные параметры',
    'battery_number': 'Номер АБ',
    'acceptance_date': 'Дата приемки',

    //BatteryInstallationHistory
    'battery': 'Серийный номер',
    'installation_location': 'Место установки',
    'installation_date': 'Дата установки',

    //TestingDBT12D
    'battery': 'АБ',
    'testing_date': 'Дата тестирования',
    'SOH': 'Состояние емкости (SOH)',
    'SOC': 'Состояние заряда (SOC)',
    'VOL': 'Напряжение',
    'R': 'Сопротивление',
};

// Поля, которые нужно скрыть
const HIDDEN_FIELDS = [
    'id',           // ID объекта
    'created_at',   // Дата создания
    'updated_at',   // Дата обновления
];

// Функция для фильтрации полей
function filterFields(data) {
    if (!data) return data;
    
    const filtered = {};
    for (const [key, value] of Object.entries(data)) {
        if (!HIDDEN_FIELDS.includes(key)) {
            filtered[key] = value;
        }
    }
    
    return filtered;
}

function showEventModal(id, eventType, eventTypeDisplay, timestamp, user, objectRepr, fullRepresentation, oldData, newData, changedFields) {
    // Определяем цвет для типа события
    let badgeColor = '#333';
    switch(eventType) {
        case 'create': badgeColor = '#00c200'; break;
        case 'update': badgeColor = '#eeee0a'; break;
        case 'delete': badgeColor = '#f73242'; break;
    }
    
    // Парсим данные
    let parsedOldData = null, parsedNewData = null;
    try {
        if (oldData && typeof oldData === 'string') parsedOldData = JSON.parse(oldData);
        else parsedOldData = oldData;
        
        if (newData && typeof newData === 'string') parsedNewData = JSON.parse(newData);
        else parsedNewData = newData;
    } catch (e) {
        console.error('Error parsing data:', e);
    }
    
    // Фильтруем данные (убираем ненужные поля)
    const filteredOldData = filterFields(parsedOldData);
    const filteredNewData = filterFields(parsedNewData);
    
    // Создаем HTML контент
    let content = `
        <div class="event-detail-item">
            <span class="event-detail-label">Тип события:</span>
            <span class="event-detail-value">
                <span class="event-type-badge" style="background: ${badgeColor}; color: ${eventType === 'update' ? '#333' : 'white'}">
                    ${eventTypeDisplay}
                </span>
            </span>
        </div>
        
        <div class="event-detail-item">
            <span class="event-detail-label">Дата и время:</span>
            <span class="event-detail-value">${timestamp}</span>
        </div>
        
        <div class="event-detail-item">
            <span class="event-detail-label">Пользователь:</span>
            <span class="event-detail-value">${user}</span>
        </div>`;
    
    // Добавляем полное описание, если есть
    if (fullRepresentation && fullRepresentation.trim() !== '') {
        content += `
        <div class="event-detail-item">
            <span class="event-detail-label">Объект:</span>
            <span class="event-detail-value">${fullRepresentation}</span>
        </div>`;
    }
    
    // Добавляем данные в зависимости от типа события
    if (eventType === 'create' && filteredNewData) {
        content += createDataSection('Созданные данные', filteredNewData, 'create');
    }
    
    if (eventType === 'update') {
        if (changedFields && changedFields.length > 0) {
            content += createChangedFieldsSection(changedFields);
        }

        if (filteredOldData && filteredNewData) {
            content += createComparisonSection(filteredOldData, filteredNewData, changedFields);
        } else if (filteredOldData) {
            content += createDataSection('Старые данные', filteredOldData, 'old');
        } else if (filteredNewData) {
            content += createDataSection('Новые данные', filteredNewData, 'new');
        }
    }
    
    if (eventType === 'delete' && filteredOldData) {
        content += createDataSection('Удалённые данные', filteredOldData, 'delete');
    }
    
    // Вставляем контент
    document.getElementById('modalContent').innerHTML = content;
    
    // Показываем модальное окно
    document.getElementById('eventModal').style.display = 'flex';
    
    // Блокируем прокрутку body
    document.body.style.overflow = 'hidden';
}

function createDataSection(title, data, dataType) {
    if (!data || Object.keys(data).length === 0) {
        return '';
    }
    
    let tableRows = '';
    for (const [key, value] of Object.entries(data)) {
        const fieldName = translateFieldName(key);
        const fieldValue = formatValue(value);
        
        tableRows += `
        <tr>
            <td>
                <div class="field-name">${fieldName}</div>
            </td>
            <td>
                <div class="field-value ${dataType}">${fieldValue}</div>
            </td>
        </tr>`;
    }
    
    return `
    <div class="data-section">
        <div class="data-section-title">${title}</div>
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Параметр</th>
                        <th>Значение</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        </div>
    </div>`;
}

function createComparisonSection(oldData, newData, changedFields) {
    if ((!oldData && !newData) || (Object.keys(oldData || {}).length === 0 && Object.keys(newData || {}).length === 0)) {
        return '';
    }
    
    // Определяем измененные поля
    const changedFieldsSet = new Set();
    try {
        if (changedFields) {
            let fields = changedFields;
            if (typeof fields === 'string') fields = JSON.parse(fields);
            
            if (Array.isArray(fields)) {
                fields.forEach(field => {
                    if (typeof field === 'object' && field.field) {
                        changedFieldsSet.add(field.field);
                    } else {
                        changedFieldsSet.add(field);
                    }
                });
            } else if (typeof fields === 'object') {
                Object.keys(fields).forEach(field => changedFieldsSet.add(field));
            }
        }
    } catch (e) {
        console.error('Error parsing changed fields:', e);
    }
    
    // Получаем все уникальные ключи
    const allKeys = new Set([
        ...Object.keys(oldData || {}),
        ...Object.keys(newData || {})
    ]);
    
    let tableRows = '';
    for (const key of Array.from(allKeys).sort()) {
        // Пропускаем скрытые поля
        if (HIDDEN_FIELDS.includes(key)) continue;
        
        const fieldName = translateFieldName(key);
        const oldValue = oldData ? oldData[key] : undefined;
        const newValue = newData ? newData[key] : undefined;
        const isChanged = changedFieldsSet.has(key);
        
        const oldValueFormatted = oldValue !== undefined ? formatValue(oldValue) : '<span style="color: #999;">—</span>';
        const newValueFormatted = newValue !== undefined ? formatValue(newValue) : '<span style="color: #999;">—</span>';
        
        tableRows += `
        <tr style="${isChanged ? 'background: #fff9e6;' : ''}">
            <td>
                <div class="field-name">
                    ${fieldName}
                    ${isChanged ? '<span style="color: #ffc107; margin-left: 8px;">✎</span>' : ''}
                </div>
            </td>
            <td style="background: ${isChanged ? '#fff3cd' : 'transparent'};">
                <div class="field-value ${isChanged ? 'old-value' : ''}">
                    ${oldValueFormatted}
                </div>
            </td>
            <td style="background: ${isChanged ? '#d4edda' : 'transparent'};">
                <div class="field-value ${isChanged ? 'new-value' : ''}">
                    ${newValueFormatted}
                </div>
            </td>
        </tr>`;
    }
    
    return `
    <div class="data-section">
        <div class="data-section-title">Сравнение данных</div>
        <div class="data-table-container">
            <table class="data-table comparison-table">
                <thead>
                    <tr>
                        <th>Параметр</th>
                        <th>Старое значение</th>
                        <th>Новое значение</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        </div>
    </div>`;
}

function createChangedFieldsSection(changedFields) {
    let fieldsHtml = '';
    let fieldsList = [];
    
    try {
        if (typeof changedFields === 'string') {
            changedFields = JSON.parse(changedFields);
        }
        
        if (Array.isArray(changedFields)) {
            changedFields.forEach(field => {
                if (typeof field === 'object' && field.field) {
                    // Фильтруем скрытые поля
                    if (!HIDDEN_FIELDS.includes(field.field)) {
                        fieldsList.push(field.field);
                    }
                } else {
                    if (!HIDDEN_FIELDS.includes(field)) {
                        fieldsList.push(field);
                    }
                }
            });
        } else if (typeof changedFields === 'object') {
            Object.keys(changedFields).forEach(field => {
                if (!HIDDEN_FIELDS.includes(field)) {
                    fieldsList.push(field);
                }
            });
        }
        
        fieldsList.forEach(field => {
            const fieldName = translateFieldName(field);
            fieldsHtml += `<span class="changed-field-item">${fieldName}</span>`;
        });
    } catch (e) {
        console.error('Error processing changed fields:', e);
    }
    
    if (fieldsList.length === 0) {
        return '';
    }
    
    return `
    <div class="changed-fields-section">
        <div class="changed-fields-title">
            Изменённые параметры (${fieldsList.length}):
        </div>
        <div class="changed-fields-list">
            ${fieldsHtml}
        </div>
    </div>`;
}

// Вспомогательные функции
function translateFieldName(field) {
    // Пробуем найти перевод в словаре
    if (FIELD_TRANSLATIONS[field]) {
        return FIELD_TRANSLATIONS[field];
    }
    
    // Если нет перевода, преобразуем snake_case/camelCase в читаемый вид
    return field
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

function formatValue(value) {
    if (value === null || value === undefined || value === 'null' || value === 'None') {
        return '<span style="color: #999; font-style: italic;">(не задано)</span>';
    }

    // ОСОБЫЙ СЛУЧАЙ: location_type
    if (value === 'virtual') {
        return 'Промежуточное место, путь';
    }
    if (value === 'container') {
        return 'Шкаф';
    }
    
    if (typeof value === 'boolean') {
        return value ? 'Да' : 'Нет';
    }
    
    if (typeof value === 'number') {
        // Форматируем числа с плавающей точкой
        return Number.isInteger(value) ? value.toString() : value.toFixed(2);
    }
    
    if (typeof value === 'object') {
        // Если это словарь с данными связанного объекта
        if (value.id !== undefined) {
            return formatRelatedField(null, value);
        }
        
        // Если это массив
        if (Array.isArray(value)) {
            if (value.length === 0) {
                return '[пусто]';
            }
            
            // Обрабатываем каждый элемент массива
            const formattedItems = value.map(item => {
                if (typeof item === 'object' && item !== null) {
                    return formatRelatedField(null, item);
                }
                return item;
            });
            
            return `[${formattedItems.join(', ')}]`;
        }
        
        return `{объект}`;
    }
    
    // Экранируем HTML
    return escapeHtml(String(value));
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function closeEventModal() {
    // Скрываем модальное окно
    document.getElementById('eventModal').style.display = 'none';
    
    // Восстанавливаем прокрутку body
    document.body.style.overflow = 'auto';
}

// Закрытие по клику на оверлей
document.getElementById('eventModal').addEventListener('click', function(event) {
    if (event.target === this) {
        closeEventModal();
    }
});

// Закрытие по клавише ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeEventModal();
    }
});

function formatRelatedField(fieldName, value) {
    // Если это словарь с данными связанного объекта
    if (typeof value === 'object' && value !== null) {
        // Проверяем различные поля по порядку
        const displayFields = [
            'serial_number',
            'battery_type_title', 
            'location_title',
            'system_title',
            'battery_number',
        ];
        
        for (const field of displayFields) {
            if (value[field]) {
                return `${value[field]}`;
            }
        }
        
        // Если есть только ID
        if (value.id) {
            return `[ID: ${value.id}]`;
        }
    }
    
    // Если это просто число (ID) - старая версия данных
    if (typeof value === 'number') {
        return `[ID: ${value}]`;
    }
    
    // Если это строка с ID
    if (typeof value === 'string' && /^\d+$/.test(value)) {
        return `[ID: ${value}]`;
    }
    
    return value;
}

// Сохраняем состояние фильтров
function toggleFilters() {
    const filterContent = document.getElementById('filterContent');
    const btn = document.querySelector('.toggle-filters-btn');
    const header = document.querySelector('.filters-header');
    
    const isVisible = filterContent.style.display === 'block';
    
    if (!isVisible) {
        // Показать
        filterContent.style.display = 'block';
        btn.innerHTML = '<i class="fas fa-chevron-up"></i> Скрыть';
        header.classList.add('open');
        localStorage.setItem('filtersVisible', 'true');
    } else {
        // Скрыть
        filterContent.style.display = 'none';
        btn.innerHTML = '<i class="fas fa-chevron-down"></i> Показать';
        header.classList.remove('open');
        localStorage.setItem('filtersVisible', 'false');
    }
}

// При загрузке
document.addEventListener('DOMContentLoaded', function() {
    const filterContent = document.getElementById('filterContent');
    const btn = document.querySelector('.toggle-filters-btn');
    const header = document.querySelector('.filters-header');
    
    if (!filterContent || !btn || !header) return;
    
    // Проверяем сохраненное состояние
    const savedState = localStorage.getItem('filtersVisible');
    
    // По умолчанию показываем если есть активные фильтры
    const hasActiveFilters = document.querySelector('.current-filter') !== null;
    
    if (savedState === 'true' || (savedState === null && hasActiveFilters)) {
        filterContent.style.display = 'block';
        btn.innerHTML = '<i class="fas fa-chevron-up"></i> Скрыть';
        header.classList.add('open');
    } else {
        filterContent.style.display = 'none';
        btn.innerHTML = '<i class="fas fa-chevron-down"></i> Показать';
        header.classList.remove('open');
    }
});

// календарь
document.addEventListener('DOMContentLoaded', function() {
    const dateFromInput = document.getElementById('dateFromInput');
    const dateToInput = document.getElementById('dateToInput');
    
    if (dateFromInput && dateToInput) {
        dateFromInput.addEventListener('change', function() {
            dateToInput.min = this.value;
        });
        
        dateToInput.addEventListener('change', function() {
            dateFromInput.max = this.value;
        });
    }
});

function showEventModalFromAttributes(element) {
    const id = element.getAttribute('data-event-id');
    const eventType = element.getAttribute('data-event-type');
    const eventTypeDisplay = element.getAttribute('data-event-type-display');
    const timestamp = element.getAttribute('data-timestamp');
    const user = element.getAttribute('data-user') || null;
    const objectRepr = element.getAttribute('data-object-repr') || null;
    const fullRepr = element.getAttribute('data-full-repr') || null;
    
    // Получаем сырые строки
    let oldDataStr = element.getAttribute('data-old-data') || '';
    let newDataStr = element.getAttribute('data-new-data') || '';
    const changedFieldsStr = element.getAttribute('data-changed-fields') || '';
    
    let oldData = null, newData = null, changedFields = null;
    
    try {
        // Функция для полного декодирования всех escape последовательностей
        const fullyDecodeString = (str) => {
            if (!str) return str;
            
            let decoded = str;
            
            // 1. Декодируем Unicode escapes (\uXXXX)
            decoded = decoded.replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => {
                return String.fromCharCode(parseInt(hex, 16));
            });
            
            // 2. Декодируем стандартные escape последовательности
            decoded = decoded
                .replace(/\\n/g, '\n')
                .replace(/\\r/g, '\r')
                .replace(/\\t/g, '\t')
                .replace(/\\"/g, '"')
                .replace(/\\'/g, "'")
                .replace(/\\\\/g, '\\');
            
            // 3. Декодируем HTML entities (&#xxxx; и &entity;)
            const textarea = document.createElement('textarea');
            textarea.innerHTML = decoded;
            decoded = textarea.value;
            
            // 4. Декодируем возможные двойные экранирования
            // Если после всех замен остались \u, пробуем еще раз
            if (decoded.includes('\\u')) {
                decoded = decoded.replace(/\\\\u([0-9a-fA-F]{4})/g, (match, hex) => {
                    return String.fromCharCode(parseInt(hex, 16));
                });
            }
            
            return decoded;
        };
        
        // Декодируем строки
        oldDataStr = fullyDecodeString(oldDataStr);
        newDataStr = fullyDecodeString(newDataStr);
        
        console.log('После декодирования:', {
            oldDataStr: oldDataStr.substring(0, 200),
            newDataStr: newDataStr.substring(0, 200)
        });
        
        // Парсим JSON
        if (oldDataStr.trim() && oldDataStr !== 'null' && oldDataStr !== 'None') {
            try {
                oldData = JSON.parse(oldDataStr);
            } catch (e) {
                console.error('JSON parse error for oldData:', e);
                // Если не JSON, пробуем как Python dict
                try {
                    const fixedStr = oldDataStr
                        .replace(/None/g, 'null')
                        .replace(/True/g, 'true')
                        .replace(/False/g, 'false');
                    oldData = new Function('return (' + fixedStr + ')')();
                } catch (e2) {
                    console.error('Python dict parse error:', e2);
                }
            }
        }
        
        if (newDataStr.trim() && newDataStr !== 'null' && newDataStr !== 'None') {
            try {
                newData = JSON.parse(newDataStr);
            } catch (e) {
                console.error('JSON parse error for newData:', e);
                try {
                    const fixedStr = newDataStr
                        .replace(/None/g, 'null')
                        .replace(/True/g, 'true')
                        .replace(/False/g, 'false');
                    newData = new Function('return (' + fixedStr + ')')();
                } catch (e2) {
                    console.error('Python dict parse error:', e2);
                }
            }
        }
        
        if (changedFieldsStr.trim() && changedFieldsStr !== 'null' && changedFieldsStr !== 'None') {
            try {
                changedFields = JSON.parse(changedFieldsStr);
            } catch (e) {
                try {
                    const fixedStr = changedFieldsStr
                        .replace(/None/g, 'null')
                        .replace(/True/g, 'true')
                        .replace(/False/g, 'false')
                        .replace(/'/g, '"');
                    changedFields = JSON.parse(fixedStr);
                } catch (e2) {
                    console.error('Changed fields parse error:', e2);
                }
            }
        }
        
        // Рекурсивно декодируем все строки в объектах
        const deepDecode = (obj) => {
            if (!obj) return obj;
            
            if (typeof obj === 'string') {
                return fullyDecodeString(obj);
            }
            
            if (Array.isArray(obj)) {
                return obj.map(item => deepDecode(item));
            }
            
            if (typeof obj === 'object') {
                const result = {};
                for (const key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        result[key] = deepDecode(obj[key]);
                    }
                }
                return result;
            }
            
            return obj;
        };
        
        if (oldData) oldData = deepDecode(oldData);
        if (newData) newData = deepDecode(newData);
        
    } catch (e) {
        console.error('Error in showEventModalFromAttributes:', e);
    }
    
    showEventModal(id, eventType, eventTypeDisplay, timestamp, user, objectRepr, fullRepr, oldData, newData, changedFields);
}