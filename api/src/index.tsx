import { Hono } from 'hono'
import { env } from 'hono/adapter'
import forge from 'node-forge'
// import { pemToBuffer } from './utils/crypto'

interface HonoEnv {
  Bindings: Env
  Variables: {
    env: Env
  }
}

const app = new Hono<HonoEnv>()

app.use('*', (c, next) => {
  c.set('env', env(c))
  return next()
})

app.get('/', (c) => {
  return c.text('Hello, Hono!')
})

app.post('/sign', async (c) => {
  const text = await c.req.arrayBuffer()
  if (!text) {
    return c.json({ error: 'Signature body is required' }, 400)
  }
  const textBuffer = text

  try {
    // Load private and public keys
    const privateKey = forge.pki.privateKeyFromPem(
      c.get('env').PASSKIT_PRIVATE_KEY
    )
    const cert = forge.pki.certificateFromPem(c.get('env').PASSKIT_CERTIFICATE)
    const wwdr = forge.pki.certificateFromPem(c.get('env').APPLE_WWDR_CERT)

    // Create signed data
    const signedData = forge.pkcs7.createSignedData()
    signedData.content = forge.util.createBuffer(textBuffer)
    signedData.addCertificate(cert)
    signedData.addCertificate(wwdr)
    signedData.addSigner({
      key: privateKey,
      certificate: cert,
      digestAlgorithm: forge.pki.oids.sha1!, // Use SHA-1 for signing
      authenticatedAttributes: [
        {
          type: forge.pki.oids.contentType!,
          value: forge.pki.oids.data!,
        },
        {
          type: forge.pki.oids.messageDigest!,
          // This will be calculated automatically
        },
        {
          type: forge.pki.oids.signingTime!,
          // This will be set automatically
        },
      ],
    })
    signedData.sign({ detached: true })

    const signatureString = forge.asn1.toDer(signedData.toAsn1())
    console.log('Detached signature created successfully')

    return c.json({
      success: true,
      signatureBase64: forge.util.encode64(signatureString.getBytes()),
    })
  } catch (error) {
    console.error('Signing error:', error)
    return c.json({ success: false, error: 'Failed to sign data' }, 500)
  }
})

export default app
