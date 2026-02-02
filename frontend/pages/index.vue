<template>
  <div />
</template>

<script>
export default {
  middleware: ['check-auth'],
  fetch({ store, redirect }) {
    if (store.getters['auth/isAuthenticated']) {
      redirect('/projects')
    } else {
      redirect('/auth')
    }
  }
}
</script>
