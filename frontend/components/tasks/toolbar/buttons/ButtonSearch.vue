<template>
  <v-tooltip bottom>
    <template #activator="{ on }">
      <v-btn icon v-on="on" @click="$emit('click:search')">
        <v-icon>
          {{ mdiMagnify }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ $t('annotation.searchTooltip') }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMagnify } from '@mdi/js'

export default Vue.extend({
  data() {
    return {
      mdiMagnify
    }
  }
})
</script>