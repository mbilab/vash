<template lang="pug">
.-sharing-editor
  .-title.-flex-container
    h3 Edit cohort Sharing
    i.large.close.icon(@click="$emit('changeComponent', 'cohort-list')")
  h4 Users:
  .-list
    .-item.-flex-container(v-for="user in unSharedUsers")
      div
        i.user.icon
          span {{ user.name }}
      i.plus.square.outline.icon(@click='addSharingCohort(user)')
  .ui.divider
  h4 Shared Users:
  .-list
    .-item.-flex-container(v-for="user in shaeedUsers")
      div
        i.user.icon
          span {{ user.name }}
      i.minus.square.outline.icon(@click='removeSharingCohort(user)')
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import axios from 'axios'
import { mapActions, mapMutations, mapState } from 'vuex'

export default {
  activated() {
    this.getFriends()
  },

  computed: {
    ...mapState(['user', 'friends']),
    cohortId() {
      return this.user.cohorts[this.cohortIdx].id
    },
    shaeedUsers() {
      return this.friends.filter(
        friend => !!friend.groups.find(group => group.id == this.cohortId)
      )
    },
    unSharedUsers() {
      return this.friends.filter(
        friend => !friend.groups.find(group => group.id == this.cohortId)
      )
    }
  },

  props: ['cohortIdx'],

  data() {
    return {}
  },

  methods: {
    ...mapActions(['getFriends']),
    ...mapMutations(['setFriends']),

    addSharingCohort(user) {
      axios.get(`/cohort/add/sharing/${this.cohortId}/${user.id}/`)

      let friends = this.friends
      friends
        .find(friend => friend.id == user.id)
        .groups.push({
          id: this.cohortId,
          name: `Cohort_${this.cohortId} Users`
        })
      this.setFriends(friends)
    },

    removeSharingCohort(user) {
      axios.get(`/cohort/remove/sharing/${this.cohortId}/${user.id}/`)

      let friends = this.friends
      let friend = friends.find(friend => friend.id == user.id)
      let groups = friend.groups
      groups = groups.filter(group => {
        group.id != this.cohortId
      })
      friend.groups = groups
      this.setFriends(friends)
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.-sharing-editor
  position: absolute
  top: 0
  left: 0
  margin-left: $COHORT-PANEL-COMPONENT-MARGIN-X
  margin-right: $COHORT-PANEL-COMPONENT-MARGIN-X
  margin-top: $COHORT-PANEL-COMPONENT-MARGIN-TOP
  margin-bottom: $COHORT-PANEL-COMPONENT-MARGIN-BOTTOM
  height: calc(100% - #{$COHORT-PANEL-COMPONENT-MARGIN-TOP + $COHORT-PANEL-COMPONENT-MARGIN-BOTTOM})
  width: calc(100% - #{2 * $COHORT-PANEL-COMPONENT-MARGIN-X})

  background-color: $LIGHT-COLOR-5
  border: $BORDER
  border-radius: .5em
  box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 1px 0px
  padding: 1em
  .-flex-container
    display: flex
    justify-content: space-between
    align-items: center
  .-title
    margin-bottom: 2em
    h3
      margin: 0
    .icon
      margin: 0
      cursor: pointer
  h4
    margin: 1em 0
  .-list
    padding: 0 2em
    .-item
      padding: 0.2em 0
    .-item > .icon
      cursor: pointer
</style>
