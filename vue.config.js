if (process.argv[2] === 'serve') {
  process.env.VUE_APP_CSRF = ''
  process.env.VUE_APP_USE_MOCKING = 'true'
} else {
  process.env.VUE_APP_CSRF = '{% csrf_token  %}'
  process.env.VUE_APP_USE_MOCKING = 'false'
}

module.exports = {
  publicPath: process.argv[2] === 'serve' ? './' : './static/',
  css: {
    loaderOptions: {
      sass: {
        prependData: '@import "~@/assets/variables.sass"'
      }
    }
  }
}
