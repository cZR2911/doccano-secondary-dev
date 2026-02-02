export const state = () => ({
  username: null,
  id: null,
  isAuthenticated: false,
  isStaff: false,
  lastCheckedAt: 0
})

export const mutations = {
  setUsername(state, username) {
    state.username = username
  },
  setUserId(state, userId) {
    state.id = userId
  },
  clearUsername(state) {
    state.username = null
  },
  setAuthenticated(state, isAuthenticated) {
    state.isAuthenticated = isAuthenticated
  },
  setIsStaff(state, isStaff) {
    state.isStaff = isStaff
  },
  setLastCheckedAt(state, lastCheckedAt) {
    state.lastCheckedAt = lastCheckedAt
  }
}

export const getters = {
  isAuthenticated(state) {
    return state.isAuthenticated
  },
  getUsername(state) {
    return state.username
  },
  getUserId(state) {
    return state.id
  },
  isStaff(state) {
    return state.isStaff
  },
  getLastCheckedAt(state) {
    return state.lastCheckedAt
  }
}

export const actions = {
  async authenticateUser({ commit }, authData) {
    try {
      await this.$repositories.auth.login(authData.username, authData.password)
      const user = await this.$repositories.user.getProfile()
      commit('setAuthenticated', true)
      commit('setUsername', user.username)
      commit('setUserId', user.id)
      commit('setIsStaff', user.isStaff)
      commit('setLastCheckedAt', Date.now())
    } catch (error) {
      commit('setAuthenticated', false)
      commit('setIsStaff', false)
      commit('clearUsername')
      commit('setUserId', null)
      commit('setLastCheckedAt', Date.now())
      throw new Error('The credential is invalid')
    }
  },
  async fetchSocialLink() {
    return await this.$repositories.auth.socialLink()
  },
  async initAuth({ commit }) {
    try {
      const user = await this.$repositories.user.getProfile()
      commit('setAuthenticated', true)
      commit('setUsername', user.username)
      commit('setUserId', user.id)
      commit('setIsStaff', user.isStaff)
    } catch {
      commit('setAuthenticated', false)
      commit('setIsStaff', false)
      commit('clearUsername')
      commit('setUserId', null)
    } finally {
      commit('setLastCheckedAt', Date.now())
    }
  },
  async logout({ commit }) {
    await this.$repositories.auth.logout()
    commit('setAuthenticated', false)
    commit('setIsStaff', false)
    commit('clearUsername')
    commit('setUserId', null)
    commit('setLastCheckedAt', Date.now())
  }
}
