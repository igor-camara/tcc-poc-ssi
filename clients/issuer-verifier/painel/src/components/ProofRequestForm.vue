<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4 pr-2">
      <div class="flex-1">
        <h2 class="text-2xl font-bold text-white mb-2">Proof Requests</h2>
        <p class="text-blue-100">Gerencie e envie solicitações de prova para holders</p>
      </div>
      <div class="flex-shrink-0">
        <Button @click="toggleFormVisibility" class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
          <Plus v-if="!showForm" class="w-4 h-4 mr-2" />
          <X v-else class="w-4 h-4 mr-2" />
          {{ showForm ? 'Cancelar' : 'Nova Solicitação' }}
        </Button>
      </div>
    </div>

    <!-- Novo Formulário (Colapsável) -->
    <div v-if="showForm" class="bg-white/10 backdrop-blur-md rounded-lg border border-white/20 p-6">
      <h3 class="text-xl font-semibold text-white mb-4">Nova Solicitação de Prova</h3>
      
      <form @submit.prevent="handleSubmit" class="space-y-5">
        <!-- Informações Básicas -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Conexão *</label>
            <Select v-model="form.connection_id" class="w-full cursor-pointer">
              <SelectTrigger class="w-full bg-blue-900/40 border border-blue-700 text-white focus:ring-blue-500">
                <SelectValue class="text-blue-200 cursor-pointer" placeholder="Selecione uma conexão ativa" />
              </SelectTrigger>
              <SelectContent class="bg-blue-950 border-blue-700">
                <SelectGroup>
                  <SelectItem v-for="conn in activeConnections" :key="conn.connection_id" :value="conn.connection_id" class="cursor-pointer hover:bg-blue-800/60 focus:bg-blue-700/80 focus:text-white hover:text-white text-white">
                    {{ conn.alias || conn.connection_id }}
                  </SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-white">Nome da Solicitação *</label>
            <Input v-model="form.name" type="text" placeholder="Ex: Verificação KYC" required class="bg-blue-900/40 border border-blue-700 text-white placeholder:text-blue-300 focus:ring-blue-500" />
          </div>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-white">Versão</label>
          <Input v-model="form.version" type="text" placeholder="1.0" class="bg-blue-900/40 border border-blue-700 text-white placeholder:text-blue-300 focus:ring-blue-500 max-w-xs" />
        </div>

        <!-- Lista de Requisitos -->
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <p class="text-sm text-blue-200">Configure os requisitos da prova</p>
            <div class="flex gap-2">
              <Button type="button" @click="addProofItem('attribute')" size="sm" class="bg-indigo-600 hover:bg-indigo-700 cursor-pointer text-white">
                <Plus class="w-4 h-4 mr-1" /> Atributo
              </Button>
              <Button type="button" @click="addProofItem('predicate')" size="sm" class="bg-orange-600 hover:bg-orange-700 cursor-pointer text-white">
                <Plus class="w-4 h-4 mr-1" /> Predicado
              </Button>
              <!--<Button type="button" @click="addProofItem('self_attested')" size="sm" class="bg-teal-600 hover:bg-teal-700 cursor-pointer text-white">
                <Plus class="w-4 h-4 mr-1" /> Auto-Atestado
              </Button>-->
            </div>
          </div>

          <div v-if="form.proofItems.length === 0" class="text-center py-12 text-blue-300 bg-blue-900/20 rounded-lg border border-blue-700/30">
            <FileSearch class="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Nenhum requisito adicionado. Clique nos botões acima para começar.</p>
          </div>

          <!-- Lista de Itens -->
          <div class="space-y-3">
            <div v-for="(item, idx) in form.proofItems" :key="idx" 
                 :class="[
                   'rounded-lg p-4 border-2 transition-all',
                   item.type === 'attribute' ? 'bg-indigo-900/30 border-indigo-600/50' : '',
                   item.type === 'predicate' ? 'bg-orange-900/30 border-orange-600/50' : '',
                   item.type === 'self_attested' ? 'bg-teal-900/30 border-teal-600/50' : ''
                 ]">
              
              <!-- Header do Item -->
              <div class="flex items-start gap-3 mb-4">
                <div class="flex-shrink-0 mt-1">
                  <div :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
                    item.type === 'attribute' ? 'bg-indigo-500 text-white' : '',
                    item.type === 'predicate' ? 'bg-orange-500 text-white' : '',
                    item.type === 'self_attested' ? 'bg-teal-500 text-white' : ''
                  ]">
                    {{ idx + 1 }}
                  </div>
                </div>
                
                <div class="flex-1 space-y-3">
                  <div class="flex items-center gap-3">
                    <span :class="[
                      'px-3 py-1 rounded-full text-xs font-semibold',
                      item.type === 'attribute' ? 'bg-indigo-500/30 text-indigo-200' : '',
                      item.type === 'predicate' ? 'bg-orange-500/30 text-orange-200' : '',
                      item.type === 'self_attested' ? 'bg-teal-500/30 text-teal-200' : ''
                    ]">
                      {{ item.type === 'attribute' ? '📋 Atributo' : item.type === 'predicate' ? '🔢 Predicado' : '✍️ Auto-Atestado' }}
                    </span>
                    <Input v-model="item.key" placeholder="Chave do requisito (ex: nome_completo)" 
                           class="flex-1 bg-blue-900/60 border border-blue-700 text-white placeholder:text-blue-400 focus:ring-blue-500" />
                  </div>

                  <!-- Atributo -->
                  <div v-if="item.type === 'attribute'" class="space-y-3 ml-2 pl-6 border-l-2 border-indigo-500/40">
                    <div class="flex justify-between items-center">
                      <label class="text-xs text-indigo-300 font-medium">Lista de Atributos:</label>
                      <Button type="button" @click="addAttribute(idx)" size="sm" variant="ghost" 
                              class="text-indigo-300 hover:text-white hover:bg-indigo-600/40 cursor-pointer">
                        <Plus class="w-3 h-3 mr-1" /> Adicionar
                      </Button>
                    </div>

                    <div class="space-y-3">
                      <div v-for="(_, aIdx) in item.attributes" :key="aIdx" class="bg-slate-800/40 rounded-lg p-3 border border-slate-700/50">
                        <template v-if="item.attributeSchemas && item.attributeSchemas[aIdx]">
                          <div class="flex items-center gap-2 mb-2">
                            <input type="checkbox" v-model="item.attributeSchemas[aIdx].enabled" :id="`attr-schema-${idx}-${aIdx}`" 
                                   class="w-4 h-4 rounded border-slate-600 bg-slate-900/60 text-indigo-500 focus:ring-indigo-500" />
                            <label :for="`attr-schema-${idx}-${aIdx}`" class="text-xs text-slate-300 cursor-pointer">
                              Vincular a um schema
                            </label>
                          </div>

                          <!-- Schema vinculado -->
                          <div v-if="item.attributeSchemas[aIdx].enabled" class="ml-6 space-y-2 mb-2">
                            <div v-if="item.attributeSchemas[aIdx].schema" 
                                 class="flex items-center justify-between bg-indigo-900/30 rounded px-3 py-2 border border-indigo-600/40">
                              <div class="text-xs font-mono text-indigo-200 flex-1 truncate">
                                {{ item.attributeSchemas[aIdx].schema.id }}
                              </div>
                              <Button type="button" @click="clearAttributeSchema(idx, aIdx)" size="sm" variant="ghost" 
                                      class="text-indigo-400 hover:text-white hover:bg-indigo-600/30 cursor-pointer ml-2">
                                <X class="w-3 h-3" />
                              </Button>
                            </div>
                            <Button v-else type="button" @click="openSchemaModalForAttribute(idx, aIdx)" size="sm" 
                                    class="bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer w-full">
                              <FileSearch class="w-4 h-4 mr-1" /> Selecionar Schema
                            </Button>
                          </div>
                        </template>

                        <!-- Campo de atributo: Select se tem schema, Input se não -->
                        <div class="flex gap-2 items-start">
                          <div class="flex-1">
                            <template v-if="item.attributeSchemas && item.attributeSchemas[aIdx]?.enabled && item.attributeSchemas[aIdx]?.schema">
                              <Select v-model="item.attributes![aIdx]" class="w-full">
                                <SelectTrigger class="bg-slate-900/60 border border-slate-600 text-white focus:ring-indigo-500">
                                  <SelectValue class="text-slate-200" placeholder="Selecione um campo do schema" />
                                </SelectTrigger>
                                <SelectContent class="bg-slate-950 border-slate-600 max-h-60">
                                  <SelectGroup>
                                    <SelectItem 
                                      v-for="attrName in item.attributeSchemas[aIdx].schema!.attrNames" 
                                      :key="attrName" 
                                      :value="attrName" 
                                      class="cursor-pointer text-white hover:bg-indigo-600/40">
                                      {{ attrName }}
                                    </SelectItem>
                                  </SelectGroup>
                                </SelectContent>
                              </Select>
                            </template>
                            <template v-else>
                              <Input v-model="item.attributes![aIdx]" placeholder="Nome do atributo (ex: nome, cpf)" 
                                     class="bg-slate-900/60 border border-slate-600 text-white placeholder:text-slate-400 focus:ring-indigo-500" />
                            </template>
                          </div>
                          <Button type="button" @click="removeAttribute(idx, aIdx)" size="sm" variant="ghost" 
                                  class="text-red-400 hover:text-white hover:bg-red-600/30 cursor-pointer">
                            <Trash2 class="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Predicado -->
                  <div v-if="item.type === 'predicate'" class="space-y-3 ml-2">
                    <div class="flex items-center gap-2">
                      <input type="checkbox" v-model="item.useSchema" :id="`schema-pred-${idx}`" 
                             class="w-4 h-4 rounded border-slate-600 bg-slate-900/60 text-orange-500 focus:ring-orange-500" />
                      <label :for="`schema-pred-${idx}`" class="text-sm text-slate-300 cursor-pointer">
                        Vincular a um schema específico
                      </label>
                    </div>

                    <div v-if="item.useSchema" class="space-y-3 pl-6 border-l-2 border-orange-500/40">
                      <div v-if="item.schema" class="flex items-center justify-between bg-orange-900/30 rounded px-3 py-2 border border-orange-600/40">
                        <div class="text-xs font-mono text-orange-200 flex-1 truncate">{{ item.schema.id }}</div>
                        <Button type="button" @click="clearSchema(idx)" size="sm" variant="ghost" class="text-orange-400 hover:text-white hover:bg-orange-600/30 cursor-pointer ml-2">
                          <X class="w-3 h-3" />
                        </Button>
                      </div>
                      <Button v-else type="button" @click="openSchemaModal(idx)" size="sm" class="bg-orange-600 hover:bg-orange-700 text-white cursor-pointer">
                        <FileSearch class="w-4 h-4 mr-1" /> Selecionar Schema
                      </Button>
                    </div>

                    <div class="pl-6 border-l-2 border-orange-500/40 space-y-2">
                      <label class="text-xs text-orange-200 font-medium">Configuração do predicado:</label>
                      <div class="flex gap-2 items-center">
                        <Input v-model="item.predicateName" placeholder="Nome do atributo" 
                               class="bg-slate-900/60 border border-slate-600 text-white placeholder:text-slate-400 focus:ring-orange-500 flex-1" />
                        <Select v-model="item.predicateType" class="w-28">
                          <SelectTrigger class="bg-slate-900/60 border border-slate-600 text-white">
                            <SelectValue class="text-slate-200" placeholder="Op" />
                          </SelectTrigger>
                          <SelectContent class="bg-slate-950 border-slate-600">
                            <SelectGroup>
                              <SelectItem class="cursor-pointer text-white" value=">=">&ge;</SelectItem>
                              <SelectItem class="cursor-pointer text-white" value=">">&gt;</SelectItem>
                              <SelectItem class="cursor-pointer text-white" value="<=">&le;</SelectItem>
                              <SelectItem class="cursor-pointer text-white" value="<">&lt;</SelectItem>
                              <SelectItem class="cursor-pointer text-white" value="==">=</SelectItem>
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                        <Input v-model="item.predicateValue" placeholder="Valor" type="number" 
                               class="bg-slate-900/60 border border-slate-600 text-white placeholder:text-slate-400 focus:ring-orange-500 w-28" />
                      </div>
                    </div>
                  </div>

                  <!-- Auto-Atestado -->
                  <div v-if="item.type === 'self_attested'" class="pl-8 border-l-2 border-teal-500/40 space-y-2">
                    <label class="text-xs text-teal-200 font-medium">
                      Nome do atributo que o holder informará livremente:
                    </label>
                    <Input v-model="item.attributeName" placeholder="Ex: telefone, cidade, profissao" 
                           class="bg-slate-900/60 border border-slate-600 text-white placeholder:text-slate-400 focus:ring-teal-500" />
                    <p class="text-xs text-teal-300/70">O holder poderá preencher este valor sem necessidade de credencial.</p>
                  </div>
                </div>

                <Button type="button" @click="removeProofItem(idx)" size="sm" variant="ghost" 
                        class="text-red-400 hover:text-white hover:bg-red-700/30 cursor-pointer flex-shrink-0">
                  <Trash2 class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Botões -->
        <div class="flex justify-end gap-3 pt-4 border-t border-blue-700/30">
          <Button type="button" @click="resetForm" class="bg-blue-600 border-blue-600 text-white hover:bg-blue-700 cursor-pointer">
            Limpar
          </Button>
          <Button 
            type="submit" 
            :disabled="!isFormValid" 
            @click="() => console.log('Botão clicado! isFormValid:', isFormValid)"
            class="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white disabled:opacity-50 disabled:cursor-not-allowed">
            <Send class="w-4 h-4 mr-2" />
            Enviar Solicitação
          </Button>
        </div>
      </form>
    </div>

    <!-- Filtros e Busca -->
    <div v-if="!showForm" class="flex gap-4 pr-2">
      <div class="flex-1 min-w-0">
        <Input v-model="searchTerm" placeholder="Buscar por nome ou connection..." class="bg-white/20 border-white/30 text-white placeholder:text-blue-100" />
      </div>
      <div class="w-40 flex-shrink-0">
        <Select v-model="stateFilter" default-value="all">
          <SelectTrigger class="w-full bg-white/20 border-white/30 text-white hover:bg-white/25 focus:ring-blue-600/50 data-[placeholder]:text-blue-100">
            <SelectValue placeholder="Filtrar por estado" />
          </SelectTrigger>
          <SelectContent class="bg-blue-900/95 backdrop-blur-md border-white/30 shadow-xl">
            <SelectGroup>
              <SelectItem value="all" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Todos</SelectItem>
              <SelectItem value="request-sent" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Enviado</SelectItem>
              <SelectItem value="presentation-received" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Recebido</SelectItem>
              <SelectItem value="done" class="!text-white hover:!bg-blue-600/60 cursor-pointer">Concluído</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>

    <!-- Lista de Proof Requests Existentes -->
    <div v-if="!showForm" class="space-y-4 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-blue-600 scrollbar-track-white/10">
      <div v-if="filteredProofExchanges.length === 0 && !appStore.isLoading" class="text-center py-12 text-blue-300">
        <FileSearch class="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Nenhuma solicitação de prova encontrada</p>
      </div>

      <div v-for="exchange in filteredProofExchanges" :key="exchange.pres_ex_id" 
           :class="[
             'relative rounded-2xl border transition-all duration-300 hover:shadow-2xl overflow-hidden',
             getProofCardClass(exchange)
           ]">
        
        <!-- Status Strip no Topo -->
        <div :class="[
          'px-6 py-3 flex items-center justify-between',
          exchange.state === 'done' && isVerified(exchange) ? 'bg-gradient-to-r from-green-600/30 to-emerald-600/30 border-b border-green-500/30' : '',
          exchange.state === 'done' && !isVerified(exchange) && exchange.verified !== null ? 'bg-gradient-to-r from-red-600/30 to-rose-600/30 border-b border-red-500/30' : '',
          exchange.state === 'abandoned' ? 'bg-gradient-to-r from-red-600/30 to-rose-600/30 border-b border-red-500/30' : '',
          exchange.state === 'request-sent' ? 'bg-gradient-to-r from-blue-600/30 to-indigo-600/30 border-b border-blue-500/30' : '',
          exchange.state === 'presentation-received' ? 'bg-gradient-to-r from-yellow-600/30 to-amber-600/30 border-b border-yellow-500/30' : ''
        ]">
          <div class="flex items-center gap-3">
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center',
              exchange.state === 'done' && isVerified(exchange) ? 'bg-green-500/30 ring-2 ring-green-400/50' : '',
              exchange.state === 'done' && !isVerified(exchange) && exchange.verified !== null ? 'bg-red-500/30 ring-2 ring-red-400/50' : '',
              exchange.state === 'abandoned' ? 'bg-red-500/30 ring-2 ring-red-400/50' : '',
              exchange.state === 'request-sent' ? 'bg-blue-500/30 ring-2 ring-blue-400/50' : '',
              exchange.state === 'presentation-received' ? 'bg-yellow-500/30 ring-2 ring-yellow-400/50' : 'bg-gray-500/30 ring-2 ring-gray-400/50'
            ]">
              <!-- Ícone Verificada -->
              <svg v-if="exchange.state === 'done' && isVerified(exchange)" class="w-6 h-6 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Ícone Falhou -->
              <svg v-else-if="exchange.state === 'done' && !isVerified(exchange) && exchange.verified !== null" class="w-6 h-6 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Ícone Abandonado -->
              <svg v-else-if="exchange.state === 'abandoned'" class="w-6 h-6 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <!-- Ícone Enviado -->
              <svg v-else-if="exchange.state === 'request-sent'" class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <!-- Ícone Recebido -->
              <svg v-else-if="exchange.state === 'presentation-received'" class="w-6 h-6 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              <!-- Ícone Default -->
              <svg v-else class="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <div class="text-white font-bold text-base">
                {{ exchange.state === 'done' && isVerified(exchange) ? '✓ Prova Verificada' : '' }}
                {{ exchange.state === 'done' && !isVerified(exchange) && exchange.verified !== null ? '✗ Verificação Falhou' : '' }}
                {{ exchange.state === 'abandoned' ? '⚠ Apresentação Abandonada' : '' }}
                {{ exchange.state === 'request-sent' ? 'Aguardando Resposta' : '' }}
                {{ exchange.state === 'presentation-received' ? 'Prova Recebida' : '' }}
              </div>
              <div class="text-xs text-white/70">
                {{ formatDate(exchange.created_at) }}
              </div>
            </div>
          </div>
          <span :class="getStateBadgeClass(exchange.state)" 
                class="px-3 py-1.5 rounded-full text-xs font-bold shadow-lg">
            {{ getStateLabel(exchange.state) }}
          </span>
        </div>

        <!-- Conteúdo do Card -->
        <div class="p-6 space-y-5">
          <!-- Informações Principais -->
          <div>
            <h3 class="text-2xl font-bold text-white mb-3">{{ exchange.pres_request.name }}</h3>
            <div class="flex items-center gap-2 text-blue-200">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span class="font-medium">Holder:</span>
              <span class="text-white font-semibold">{{ getConnectionAlias(exchange.connection_id) }}</span>
            </div>
          </div>

          <!-- Mensagem de Erro para Abandoned -->
          <div v-if="exchange.state === 'abandoned'" 
               class="bg-gradient-to-br from-red-900/40 to-rose-900/40 border-2 border-red-500/60 rounded-xl p-5">
            <div class="flex items-start gap-3">
              <svg class="w-6 h-6 text-red-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div class="flex-1">
                <h4 class="text-base font-bold text-red-200 mb-1">Apresentação Abandonada</h4>
                <p class="text-sm text-red-300/90">{{ exchange.error_msg || 'O holder não conseguiu gerar a apresentação' }}</p>
              </div>
            </div>
          </div>

          <!-- Mensagens de Erro -->
          <div v-if="!isVerified(exchange) && exchange.verified_msgs && exchange.verified_msgs.length > 0" 
               class="bg-gradient-to-br from-red-900/40 to-rose-900/40 border-2 border-red-500/60 rounded-xl p-5">
            <div class="flex items-start gap-3 mb-3">
              <svg class="w-6 h-6 text-red-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div class="flex-1">
                <h4 class="text-base font-bold text-red-200 mb-1">Problemas Detectados</h4>
                <p class="text-sm text-red-300/80">A prova não passou nas seguintes verificações:</p>
              </div>
            </div>
            <ul class="space-y-2 pl-9">
              <li v-for="(msg, idx) in exchange.verified_msgs" :key="idx" 
                  class="text-sm text-red-100 bg-red-950/50 rounded-lg px-4 py-2.5 border border-red-600/40">
                {{ formatErrorMessage(msg) }}
              </li>
            </ul>
          </div>

          <!-- Requisitos e Respostas em Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <!-- Requisitos -->
            <div class="bg-blue-900/20 rounded-xl p-5 border border-blue-600/30">
              <h4 class="text-sm font-bold text-blue-300 mb-4 flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                O que foi solicitado
              </h4>
              
              <!-- Atributos Solicitados -->
              <div v-if="Object.keys(exchange.pres_request.requested_attributes).length > 0" class="space-y-3 mb-4">
                <div class="text-xs font-semibold text-indigo-300 uppercase tracking-wide mb-2">📋 Atributos</div>
                <div v-for="(attr, key) in exchange.pres_request.requested_attributes" :key="key" 
                     class="bg-indigo-900/40 border border-indigo-600/50 rounded-lg px-3 py-2">
                  <div class="text-xs text-indigo-300 mb-0.5">{{ key }}</div>
                  <div class="text-sm text-white font-medium">
                    <span v-if="attr.name">{{ attr.name }}</span>
                    <span v-else-if="attr.names">{{ attr.names.join(', ') }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Predicados Solicitados -->
              <div v-if="Object.keys(exchange.pres_request.requested_predicates).length > 0" class="space-y-3">
                <div class="text-xs font-semibold text-orange-300 uppercase tracking-wide mb-2">🔢 Predicados</div>
                <div v-for="(pred, key) in exchange.pres_request.requested_predicates" :key="key" 
                     class="bg-orange-900/40 border border-orange-600/50 rounded-lg px-3 py-2">
                  <div class="text-xs text-orange-300 mb-0.5">{{ key }}</div>
                  <div class="text-sm text-white font-medium font-mono">
                    {{ pred.name }} {{ pred.p_type }} {{ pred.p_value }}
                  </div>
                </div>
              </div>

              <div v-if="Object.keys(exchange.pres_request.requested_attributes).length === 0 && Object.keys(exchange.pres_request.requested_predicates).length === 0" 
                   class="text-center py-4 text-blue-300/50 text-sm">
                Nenhum requisito específico
              </div>
            </div>

            <!-- Respostas -->
            <div class="bg-green-900/20 rounded-xl p-5 border border-green-600/30">
              <h4 class="text-sm font-bold text-green-300 mb-4 flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                O que foi apresentado
              </h4>

              <div v-if="!exchange.pres" class="text-center py-8 text-green-300/50 text-sm">
                <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Aguardando prova do holder
              </div>

              <!-- Atributos Revelados -->
              <div v-if="hasRevealedAttrs(exchange)" class="space-y-3 mb-4">
                <div class="text-xs font-semibold text-green-300 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Revelados
                </div>
                <div v-for="(attr, key) in exchange.pres.revealed_attrs" :key="key" 
                     class="bg-green-900/40 border border-green-600/50 rounded-lg px-3 py-2">
                  <div class="text-xs text-green-300 mb-0.5">{{ key }}</div>
                  <div class="text-sm text-white font-semibold">{{ attr.raw }}</div>
                </div>
              </div>

              <!-- Atributos Não Revelados -->
              <div v-if="hasUnrevealedAttrs(exchange)" class="space-y-3 mb-4">
                <div class="text-xs font-semibold text-yellow-300 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  Não Revelados (ZKP)
                </div>
                <div v-for="(_, key) in exchange.pres.unrevealed_attrs" :key="key" 
                     class="bg-yellow-900/40 border border-yellow-600/50 rounded-lg px-3 py-2">
                  <div class="text-xs text-yellow-300 mb-0.5">{{ key }}</div>
                  <div class="text-xs text-yellow-200 italic">Comprovado via Zero-Knowledge Proof</div>
                </div>
              </div>

              <!-- Predicados -->
              <div v-if="hasPredicates(exchange)" class="space-y-3">
                <div class="text-xs font-semibold text-blue-300 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Predicados Validados
                </div>
                <div v-for="(_, key) in exchange.pres.predicates" :key="key" 
                     class="bg-blue-900/40 border border-blue-600/50 rounded-lg px-3 py-2">
                  <div class="text-xs text-blue-300 mb-0.5">{{ key }}</div>
                  <template v-if="exchange.pres_request.requested_predicates[key]">
                    <div class="text-xs text-white">
                      {{ exchange.pres_request.requested_predicates[key].name }}
                      {{ exchange.pres_request.requested_predicates[key].p_type }}
                      {{ exchange.pres_request.requested_predicates[key].p_value }}
                      <span class="text-blue-300 ml-1">✓</span>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de busca de schemas -->
    <SchemaSearchModal v-if="showSchemaModal" :onSelect="handleSchemaSelect" :onClose="closeSchemaModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Trash2, X, Send, FileSearch } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useConnectionStore, useProofStore, useAppStore } from '@/stores'
import SchemaSearchModal from '@/components/SchemaSearchModal.vue'

const proofStore = useProofStore()
const connectionStore = useConnectionStore()
const appStore = useAppStore()

// UI State
const showForm = ref(false)
const searchTerm = ref('')
const stateFilter = ref('all')

// Interfaces
interface AttributeSchema {
  enabled: boolean
  schema?: {
    id: string
    attrNames: string[]
  }
}

interface ProofItem {
  type: 'attribute' | 'predicate' | 'self_attested'
  key: string
  
  // Para atributos
  attributes?: string[]
  attributeSchemas?: AttributeSchema[]
  
  // Para predicados
  useSchema?: boolean
  schema?: {
    id: string
    attrNames: string[]
  }
  predicateName?: string
  predicateType?: string
  predicateValue?: string | number
  
  // Para self-attested
  attributeName?: string
}

interface ProofRequestForm {
  connection_id: string
  name: string
  version: string
  proofItems: ProofItem[]
}

// Form State
const form = ref<ProofRequestForm>({
  connection_id: '',
  name: '',
  version: '1.0',
  proofItems: []
})

// Schema Modal State
const showSchemaModal = ref(false)
const schemaModalIndex = ref(-1)
const schemaModalAttributeIndex = ref(-1)

// Computed
const activeConnections = computed(() => {
  const active = connectionStore.connections.filter(c => c.state === 'active' || c.state === 'response')
  console.log('Active connections:', active)
  return active
})

const isFormValid = computed(() => {
  const hasConnection = !!form.value.connection_id
  const hasName = form.value.name.trim() !== ''
  const hasItems = form.value.proofItems.length > 0
  
  console.log('Validação do form:', {
    hasConnection,
    hasName,
    hasItems,
    connection_id: form.value.connection_id,
    name: form.value.name,
    proofItems: form.value.proofItems
  })
  
  return hasConnection && hasName && hasItems
})

const filteredProofExchanges = computed(() => {
  let filtered = proofStore.proofExchanges

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(
      ex =>
        ex.pres_request.name.toLowerCase().includes(search) ||
        ex.connection_id.toLowerCase().includes(search) ||
        getConnectionAlias(ex.connection_id).toLowerCase().includes(search)
    )
  }

  // Filter by state
  if (stateFilter.value !== 'all') {
    filtered = filtered.filter(ex => ex.state === stateFilter.value)
  }

  return filtered
})

// UI Actions
function toggleFormVisibility() {
  showForm.value = !showForm.value
  if (!showForm.value) {
    resetForm()
  }
}

function resetForm() {
  form.value = {
    connection_id: '',
    name: '',
    version: '1.0',
    proofItems: []
  }
}

// Proof Item Actions
function addProofItem(type: 'attribute' | 'predicate' | 'self_attested') {
  const newItem: ProofItem = {
    type,
    key: '',
  }

  if (type === 'attribute') {
    newItem.attributes = ['']
    newItem.attributeSchemas = [{ enabled: false }]
  } else if (type === 'predicate') {
    newItem.useSchema = false
    newItem.predicateName = ''
    newItem.predicateType = '>='
    newItem.predicateValue = ''
  } else if (type === 'self_attested') {
    newItem.attributeName = ''
  }

  form.value.proofItems.push(newItem)
}

function removeProofItem(idx: number) {
  form.value.proofItems.splice(idx, 1)
}

function addAttribute(idx: number) {
  const item = form.value.proofItems[idx]
  if (item && item.attributes && item.attributeSchemas) {
    item.attributes.push('')
    item.attributeSchemas.push({ enabled: false })
  }
}

function removeAttribute(itemIdx: number, attrIdx: number) {
  const item = form.value.proofItems[itemIdx]
  if (item && item.attributes && item.attributeSchemas) {
    item.attributes.splice(attrIdx, 1)
    item.attributeSchemas.splice(attrIdx, 1)
  }
}

// Schema Modal Actions
function openSchemaModal(idx: number) {
  schemaModalIndex.value = idx
  schemaModalAttributeIndex.value = -1
  showSchemaModal.value = true
}

function openSchemaModalForAttribute(itemIdx: number, attrIdx: number) {
  schemaModalIndex.value = itemIdx
  schemaModalAttributeIndex.value = attrIdx
  showSchemaModal.value = true
}

function closeSchemaModal() {
  showSchemaModal.value = false
  schemaModalAttributeIndex.value = -1
}

function clearSchema(idx: number) {
  const item = form.value.proofItems[idx]
  if (item) {
    item.schema = undefined
  }
}

function clearAttributeSchema(itemIdx: number, attrIdx: number) {
  const item = form.value.proofItems[itemIdx]
  if (item && item.attributeSchemas && item.attributeSchemas[attrIdx]) {
    item.attributeSchemas[attrIdx].schema = undefined
  }
}

function handleSchemaSelect(schema: any) {
  const item = form.value.proofItems[schemaModalIndex.value]
  if (!item) return

  // Schema para atributo individual
  if (schemaModalAttributeIndex.value >= 0) {
    const attrSchemaArray = item.attributeSchemas
    const attrSchema = attrSchemaArray?.[schemaModalAttributeIndex.value]
    if (attrSchema) {
      attrSchema.schema = {
        id: schema.id,
        attrNames: schema.attrNames || []
      }
    }
  } else {
    // Schema para predicado
    item.schema = {
      id: schema.id,
      attrNames: schema.attrNames || []
    }
  }
  
  closeSchemaModal()
}

// Form Submit
async function handleSubmit() {
  console.log('=== INICIANDO SUBMIT ===')
  console.log('Form data:', JSON.stringify(form.value, null, 2))
  
  const requested_attributes: Record<string, any> = {}
  const requested_predicates: Record<string, any> = {}
  const self_attested_attributes: Record<string, string> = {}

  for (const item of form.value.proofItems) {
    console.log('Processando item:', item)
    if (!item.key || !item.key.trim()) {
      console.log('Item ignorado: key vazia')
      continue
    }

    if (item.type === 'attribute') {
      const names = (item.attributes || []).filter(a => a && a.trim())
      if (names.length === 0) continue

      // Verificar se há schemas individuais configurados
      const hasIndividualSchemas = item.attributeSchemas?.some(s => s.enabled && s.schema)

      if (hasIndividualSchemas && item.attributeSchemas) {
        // Agrupar atributos por schema
        const schemaGroups = new Map<string | null, string[]>()
        
        names.forEach((name, idx) => {
          const attrSchema = item.attributeSchemas![idx]
          const schemaId = attrSchema?.enabled && attrSchema.schema ? attrSchema.schema.id : null
          
          if (!schemaGroups.has(schemaId)) {
            schemaGroups.set(schemaId, [])
          }
          schemaGroups.get(schemaId)!.push(name)
        })

        // Se todos os atributos têm o mesmo schema (ou nenhum), usar um único grupo
        if (schemaGroups.size === 1) {
          const firstEntry = Array.from(schemaGroups.entries())[0]
          if (firstEntry) {
            const [schemaId, attrs] = firstEntry
            
            if (attrs.length === 1) {
              requested_attributes[item.key] = {
                name: attrs[0],
                restrictions: schemaId ? [{ schema_id: schemaId }] : undefined
              }
            } else {
              requested_attributes[item.key] = {
                names: attrs,
                restrictions: schemaId ? [{ schema_id: schemaId }] : undefined
              }
            }
          }
        } else {
          // Schemas diferentes: criar grupos separados
          let groupIndex = 1
          schemaGroups.forEach((attrs, schemaId) => {
            const groupKey = schemaGroups.size > 1 ? `${item.key}_${groupIndex}` : item.key
            
            if (attrs.length === 1) {
              requested_attributes[groupKey] = {
                name: attrs[0],
                restrictions: schemaId ? [{ schema_id: schemaId }] : undefined
              }
            } else {
              requested_attributes[groupKey] = {
                names: attrs,
                restrictions: schemaId ? [{ schema_id: schemaId }] : undefined
              }
            }
            groupIndex++
          })
        }
      } else {
        // Sem schemas individuais - grupo único com o identificador original
        if (names.length === 1) {
          requested_attributes[item.key] = {
            name: names[0]
          }
        } else {
          requested_attributes[item.key] = {
            names
          }
        }
      }
    } else if (item.type === 'predicate') {
      if (!item.predicateName || !item.predicateType || item.predicateValue === '' || item.predicateValue === undefined) continue

      const predicate: any = {
        name: item.predicateName,
        p_type: item.predicateType,
        p_value: Number(item.predicateValue)
      }

      if (item.useSchema && item.schema) {
        predicate.restrictions = [{ schema_id: item.schema.id }]
      }

      requested_predicates[item.key] = predicate
    } else if (item.type === 'self_attested') {
      if (!item.attributeName || !item.attributeName.trim()) continue
      self_attested_attributes[item.key] = item.attributeName
    }
  }

  console.log('Requested Attributes:', requested_attributes)
  console.log('Requested Predicates:', requested_predicates)
  console.log('Self Attested:', self_attested_attributes)

  const payload: any = {
    connection_id: form.value.connection_id,
    proof_request: {
      name: form.value.name,
      version: form.value.version,
      requested_attributes,
      requested_predicates
    }
  }

  // Adicionar self_attested_attributes apenas se houver itens
  if (Object.keys(self_attested_attributes).length > 0) {
    payload.proof_request.self_attested_attributes = self_attested_attributes
  }

  console.log('Payload final:', JSON.stringify(payload, null, 2))

  const result = await proofStore.sendProofRequest(payload)
  
  console.log('Resultado:', result)

  if (result !== null) {
    resetForm()
    showForm.value = false
  }
}

// Helper Functions
function getConnectionAlias(connectionId: string): string {
  const conn = connectionStore.connections.find(c => c.connection_id === connectionId)
  return conn?.alias || connectionId
}

function getStateBadgeClass(state: string): string {
  const classes: Record<string, string> = {
    'request-sent': 'bg-blue-500/20 text-blue-300',
    'presentation-received': 'bg-yellow-500/20 text-yellow-300',
    'done': 'bg-green-500/20 text-green-300',
    'abandoned': 'bg-red-500/20 text-red-300'
  }
  return classes[state] || 'bg-gray-500/20 text-gray-300'
}

function getStateLabel(state: string): string {
  const labels: Record<string, string> = {
    'request-sent': 'Enviado',
    'presentation-received': 'Recebido',
    'done': 'Concluído',
    'abandoned': 'Abandonado'
  }
  return labels[state] || state
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatErrorMessage(msg: string): string {
  // Formata mensagens de erro técnicas para português
  const translations: Record<string, string> = {
    'VALUE_ERROR': 'Erro de Valor',
    'Missing requested attribute group': 'Grupo de atributos não fornecido',
    'RMV_GLB_NRI': 'Falha na validação da prova',
    'ENCODING_ERROR': 'Erro de codificação',
    'MISSING_ESSENTIAL_ATTRIBUTES': 'Atributos essenciais faltando',
    'INVALID_PREDICATE': 'Predicado inválido',
    'SCHEMA_MISMATCH': 'Schema incompatível',
    'CREDENTIAL_REVOKED': 'Credencial revogada'
  }
  
  let formatted = msg
  for (const [key, value] of Object.entries(translations)) {
    formatted = formatted.replace(new RegExp(key, 'gi'), value)
  }
  
  // Remove :: e substitui por :
  formatted = formatted.replace('::', ': ')
  
  return formatted
}

// Funções auxiliares para verificação
function isVerified(exchange: any): boolean {
  // O campo verified pode ser string 'true'/'false' ou booleano
  return exchange.verified === 'true' || exchange.verified === true
}

function getProofCardClass(exchange: any): string {
  if (exchange.state === 'abandoned') {
    return 'bg-gradient-to-br from-red-900/20 to-rose-900/20 border-red-500/30 hover:border-red-400/50'
  }
  if (exchange.state === 'done') {
    if (isVerified(exchange)) {
      return 'bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-green-500/30 hover:border-green-400/50'
    } else if (exchange.verified !== null) {
      return 'bg-gradient-to-br from-red-900/20 to-rose-900/20 border-red-500/30 hover:border-red-400/50'
    }
  }
  return 'bg-white/10 border-white/20 hover:border-white/30'
}

function hasRevealedAttrs(exchange: any): boolean {
  return exchange.pres?.revealed_attrs && Object.keys(exchange.pres.revealed_attrs).length > 0
}

function hasUnrevealedAttrs(exchange: any): boolean {
  return exchange.pres?.unrevealed_attrs && Object.keys(exchange.pres.unrevealed_attrs).length > 0
}

function hasPredicates(exchange: any): boolean {
  return exchange.pres?.predicates && Object.keys(exchange.pres.predicates).length > 0 &&
         exchange.pres_request?.requested_predicates
}

// Lifecycle
onMounted(async () => {
  await connectionStore.fetchAll()
  await proofStore.fetchAll({ descending: true, limit: 100, offset: 0 })
})
</script>
