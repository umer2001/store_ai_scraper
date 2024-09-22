// context.js
const context = {};

module.exports = {
  setContext: (key, value) => {
    context[key] = value;
  },
  getContext: (key) => {
    return context[key];
  },
  clearContext: () => {
    for (let key in context) {
      delete context[key];
    }
  }
};
