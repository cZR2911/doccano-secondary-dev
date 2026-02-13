<template>
  <v-item-group v-model="selected" mandatory @change="onSelectionChange">
    <v-row no-gutters>
      <v-col v-for="(item, i) in visibleProjectTypes" :key="i">
        <v-item v-slot="{ active, toggle }">
          <v-card class="mb-6 me-6" max-width="350" outlined>
            <task-preview :type="item" @click="toggle" />
            <v-card-title>
              <v-icon v-if="active">
                {{ mdiCheckBold }}
              </v-icon>
              {{ translateTypeName(item, $t('overview.projectTypes')) }}
              <span v-if="item === 'KnowledgeCorrection'" class="ml-2 grey--text text--darken-1">
                (测试)
              </span>
            </v-card-title>
          </v-card>
        </v-item>
      </v-col>
    </v-row>
  </v-item-group>
</template>

<script lang="ts">
import { mdiCheckBold } from '@mdi/js'
import Vue from 'vue'
import TaskPreview from './TaskPreview.vue'
import {
  allProjectTypes,
  DocumentClassification,
  ProjectType
} from '~/domain/models/project/project'

export default Vue.extend({
  components: {
    TaskPreview
  },
  props: {
    value: {
      type: String,
      default: DocumentClassification,
      required: true
    }
  },

  data() {
    return {
      mdiCheckBold,
      allProjectTypes,
      selected: 0
    }
  },

  computed: {
    visibleProjectTypes() {
      const hidden = [
        'ImageClassification',
        'ImageCaptioning',
        'BoundingBox',
        'Segmentation',
        'Speech2text'
      ]
      return allProjectTypes.filter((type) => !hidden.includes(type))
    }
  },

  methods: {
    translateTypeName(type: ProjectType, types: any): string {
      const index = allProjectTypes.indexOf(type)
      return types[index]
    },

    onSelectionChange() {
      this.$emit('input', this.visibleProjectTypes[this.selected])
    }
  }
})
</script>
