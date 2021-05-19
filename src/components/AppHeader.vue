<template lang="pug">
.-header
  .-tittle
    span Vash
  .-user(@click='logoutDropdown = !logoutDropdown')
    i.large.user.circle.icon
    | {{ user.username }}
  .-dropdown(:class='{dropdown: logoutDropdown}')
    .-info
      i.large.user.circle.icon
      | {{ user.username }}
    .-logout(@click='logout')
      i.large.sign-out.icon
      | Logout
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import axios from 'axios'
import { mapState } from 'vuex'

export default {
  computed: { ...mapState(['user']) },

  data() {
    return {
      logoutDropdown: false
    }
  },

  methods: {
    logout() {
      axios.post('/logout/').then(() => {
        location.reload()
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@import "../assets/variables.sass"

$header-bottom-border: 2px solid rgba(34, 36, 38, 0.15)
$tittle-color: $LIGHT-COLOR-4
$header-color: $DARK-COLOR-2

.-header
  height: $HEADER-HEIGHT
  line-height: $HEADER-HEIGHT
  border-bottom: $header-bottom-border
  background-color: $header-color
  display: flex
  justify-content: space-between

.-tittle
  color: $tittle-color
  padding: 0 .7rem 0 .7rem
  font-size: 1.5em

.-user
  cursor: pointer
  height: $HEADER-HEIGHT
  color:  $tittle-color
  border-bottom: $header-bottom-border
  padding: 0 1em

.-dropdown
  position: absolute
  right: 1em
  top: 64px
  width: 10em
  z-index: 10
  border: $BORDER
  border-radius: .5em
  color: $header-color
  background-color: $tittle-color
  display: none
  .-info
    padding: 1em
    margin: auto
    border-bottom: $BORDER
  .-logout
    padding: 0 1em
    cursor: pointer
    &:hover
      color: darken($header-color, 10%)
      background-color: darken($tittle-color, 10%)
  &.dropdown
    display: flex
    flex-direction: column
</style>
