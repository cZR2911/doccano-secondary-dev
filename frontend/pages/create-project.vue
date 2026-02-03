<!-- Force re-watch -->
<template>
  <v-card>
    <v-card-title>{{ $t('overview.createProjectTitle') }}</v-card-title>
    <v-card-text>
      <v-form v-model="valid">
        <project-type-field v-model="editedItem.projectType" />
        <project-name-field v-model="editedItem.name" outlined autofocus />
        <project-description-field v-model="editedItem.description" outlined />
        <tag-list v-model="editedItem.tags" outlined />
        <v-checkbox
          v-if="showExclusiveCategories"
          v-model="editedItem.exclusiveCategories"
          :label="$t('overview.allowSingleLabel')"
        />
        <v-checkbox
          v-if="_canDefineLabel"
          v-model="editedItem.allowMemberToCreateLabelType"
          :label="$t('settings.allowMemberToCreateLabelType')"
        />
        <template v-if="isSequenceLabelingProject">
          <v-checkbox
            v-model="editedItem.allowOverlappingSpans"
            :label="$t('overview.allowOverlappingSpans')"
          />
          <v-img
            :src="require('~/assets/project/creation.gif')"
            height="200"
            position="left"
            contain
          />
          <v-checkbox v-model="editedItem.useRelation" :label="$t('overview.useRelation')" />
          <v-checkbox
            v-model="editedItem.enableGraphemeMode"
            :label="$t('overview.graphemeMode')"
          />
        </template>
        <random-order-field v-model="editedItem.enableRandomOrder" />
        <sharing-mode-field v-model="editedItem.enableSharingMode" />
      </v-form>
    </v-card-text>
    <v-card-actions class="ps-4">
      <v-btn
        :disabled="!valid || loading"
        :loading="loading"
        color="primary"
        style="text-transform: none"
        outlined
        @click="create"
      >
        {{ $t('generic.create') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import ProjectDescriptionField from '~/components/project/ProjectDescriptionField.vue'
import ProjectNameField from '~/components/project/ProjectNameField.vue'
import ProjectTypeField from '~/components/project/ProjectTypeField.vue'
import RandomOrderField from '~/components/project/RandomOrderField.vue'
import SharingModeField from '~/components/project/SharingModeField.vue'
import TagList from '~/components/project/TagList.vue'
import {
  DocumentClassification,
  ImageClassification,
  SequenceLabeling,
  canDefineLabel
} from '~/domain/models/project/project'

const initializeProject = () => {
  return {
    name: '',
    description: '',
    projectType: DocumentClassification,
    enableRandomOrder: false,
    enableSharingMode: false,
    exclusiveCategories: false,
    allowOverlappingSpans: false,
    enableGraphemeMode: false,
    useRelation: false,
    tags: [] as string[],
    guideline: '',
    allowMemberToCreateLabelType: false
  }
}

export default Vue.extend({
  components: {
    ProjectTypeField,
    ProjectNameField,
    ProjectDescriptionField,
    RandomOrderField,
    SharingModeField,
    TagList
  },

  layout: 'projects',

  middleware: ['check-auth', 'auth'],

  data() {
    return {
      valid: false,
      loading: false,
      editedItem: initializeProject()
    }
  },

  computed: {
    showExclusiveCategories(): boolean {
      return [DocumentClassification, ImageClassification].includes(this.editedItem.projectType)
    },
    isSequenceLabelingProject(): boolean {
      return this.editedItem.projectType === SequenceLabeling
    },
    _canDefineLabel(): boolean {
      return canDefineLabel(this.editedItem.projectType as any)
    }
  },

  methods: {
    async create() {
      if (!this.valid) {
        alert('请填写所有必填项（名称和描述）')
        return
      }

      this.loading = true
      try {
        const project = await this.$services.project.create(this.editedItem)
        if (!project || !project.id) {
          console.error('Project creation failed or returned invalid ID:', project)
          alert('创建失败：服务器返回的数据不完整')
          return
        }
        const path = this.localePath({ name: 'projects-id', params: { id: project.id.toString() } })
        this.$router.push(path)
        this.$nextTick(() => {
          this.editedItem = initializeProject()
        })
      } catch (error: any) {
        console.error('Full error object:', error)
        let errorMsg = '未知错误'
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorMsg = `服务器错误 (${error.response.status}): ${JSON.stringify(error.response.data)}`
        } else if (error.request) {
          // The request was made but no response was received
          errorMsg = '网络错误：无法连接到服务器，请检查后端服务是否启动'
        } else {
          // Something happened in setting up the request that triggered an Error
          errorMsg = error.message || '未知错误'
        }
        alert('创建项目时发生错误：' + errorMsg)
      } finally {
        this.loading = false
      }
    }
  }
})
</script>
