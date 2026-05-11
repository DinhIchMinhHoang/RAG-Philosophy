const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const current = LEVELS[localStorage.getItem('logLevel')] ?? LEVELS.info;

function format(level, ...args) {
    return [`[${level.toUpperCase()}]`, ...args];
}

export const logger = {
    debug: (...a) => { if (current <= LEVELS.debug) console.debug(...format('debug', ...a)); },
    info:  (...a) => { if (current <= LEVELS.info)  console.info(...format('info', ...a)); },
    warn:  (...a) => { if (current <= LEVELS.warn)  console.warn(...format('warn', ...a)); },
    error: (...a) => { if (current <= LEVELS.error) console.error(...format('error', ...a)); },
};
