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

    //InstallationLocation
    'location_title': 'Название места установки',
    'system_title': 'Название системы',
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
