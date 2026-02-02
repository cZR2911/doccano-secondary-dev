<template>
  <v-card>
    <v-toolbar v-if="title" color="primary white--text" flat>
      <v-toolbar-title>{{ title }}</v-toolbar-title>
    </v-toolbar>
    <v-card-text class="text--primary mt-3 pl-4">
      <slot name="content" />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn
        v-if="cancelText"
        class="text-capitalize"
        text
        color="primary"
        data-test="cancel-button"
        @click="cancel"
      >
        {{ cancelText }}
      </v-btn>
      <v-btn
        v-if="agreeText"
        :disabled="disabled"
        class="text-none"
        :color="agreeColor"
        :text="!contained"
        :depressed="contained"
        :block="block"
        @click="agree"
      >
        {{ agreeText }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  props: {
    title: {
      type: String,
      default: '',
      required: true
    },
    cancelText: {
      type: String,
      default: ''
    },
    agreeText: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    agreeColor: {
      type: String,
      default: 'primary'
    },
    contained: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    }
  },

  methods: {
    agree() {
      this.$emit('agree')
    },
    cancel() {
      this.$emit('cancel')
    }
  }
})
</script>
