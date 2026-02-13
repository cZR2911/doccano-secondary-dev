<template>
  <v-app id="inspire">
    <v-main class="login-background">
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <div class="text-center mb-10">
              <img
                src="~/assets/logo.png"
                height="80"
                class="mb-4 elevation-2 rounded-circle white"
                style="padding: 10px;"
              />
              <h1 class="white--text font-weight-bold text-h4 mb-2 text-shadow">
                默联数据标注平台
              </h1>
              <p class="white--text subtitle-1 opacity-80">
                高效、智能、开源的数据标注解决方案
              </p>
            </div>
            <form-login
              :login="authenticateUser"
              class="elevation-12 rounded-lg overflow-hidden"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue'
import { mapActions } from 'vuex'
import FormLogin from '@/components/auth/FormLogin.vue'

export default Vue.extend({
  components: {
    FormLogin
  },

  methods: {
    ...mapActions('auth', ['authenticateUser'])
  }
})
</script>

<style scoped>
.login-background {
  /* 方案一：科技蓝紫（改良版 - 更稳重） */
  background: linear-gradient(135deg, #363795 0%, #005C97 100%);

  /* 方案二：深邃极光 */
  /* background: linear-gradient(to right, #0f2027, #203a43, #2c5364); */

  /* 方案三：日落大道 */
  /* background: linear-gradient(to right, #0b486b, #f56217); */

  /* 方案四：酷炫黑金 */
  /* background: linear-gradient(to right, #232526, #414345); */

  position: relative;
}

.text-shadow {
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.opacity-80 {
  opacity: 0.8;
}
</style>
