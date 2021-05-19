<template lang="pug">
.ui.card.error.form
  .content: .header #[i.yellow.bolt.icon]VASH
  .content
    .field
      label User Name
      input(
        @keyup='setLoginError("")'
        @keyup.enter='login({ username, password })'
        type='text'
        v-model='username'
        )
    .field
      label Password
      input(
        @keyup='setLoginError("")'
        @keyup.enter='login({ username, password })'
        type='password'
        v-model='password'
        )
    .ui.error.message {{ loginError }}
    .ui.primary.button(@click='login({ username, password })') Login
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex'
export default {
  computed: mapState(['loginError']),

  data() {
    return {
      err: '',
      username: '',
      password: ''
    }
  },

  methods: {
    ...mapActions(['login']),
    ...mapMutations(['setLoginError'])
  }
}
</script>

<style lang="sass" scoped>
.ui.card
  left: 50%
  position: absolute
  top: 50%
  transform: translate(-50%, -50%)
</style>
