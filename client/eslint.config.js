import antfu from '@antfu/eslint-config'

export default antfu({
  vue: true,
  typescript: false,
  formatters: true,
  rules: {
    'no-console': 'warn',
    'vue/max-attributes-per-line': 'off'
  }
})