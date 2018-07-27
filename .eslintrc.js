module.exports = {
  extends: 'google',
  parser: 'babel-eslint',
  rules: {
    strict: 0,
    'no-unused-vars': ['error', {varsIgnorePattern: 'MDC'}],
    'arrow-parens': 'off',
    'require-jsdoc': 'off',
  },
};
