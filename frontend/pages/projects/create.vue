<template>
  <div />
</template>

<script>
export default {
  middleware({ app, redirect }) {
    return redirect(app.localePath('/create-project'))
  }
}
</script>
