import { ProjectType } from '@/domain/models/project/project'

export const getLinkToAnnotationPage = (
  projectId: number | string,
  projectType: ProjectType
): string => {
  const mapping = {
    DocumentClassification: 'text-classification',
    SequenceLabeling: 'sequence-labeling',
    Seq2seq: 'sequence-to-sequence',
    IntentDetectionAndSlotFilling: 'intent-detection-and-slot-filling',
    ImageClassification: 'image-classification',
    ImageCaptioning: 'image-captioning',
    BoundingBox: 'object-detection',
    Segmentation: 'segmentation',
    Speech2text: 'speech-to-text',
    // [EXPERIMENTAL-FEATURE-START]
    KnowledgeCorrection: 'sequence-labeling'
    // [EXPERIMENTAL-FEATURE-END]
  }
  const link = `/projects/${projectId}/${mapping[projectType]}`
  return link
}
