const  express = require('express')
var amqp = require('amqplib/callback_api');


const app = express()

const port = 3001

app.get('/website',(req,res)=>{

    const domain = req.query.domain
    const bool = req.query.bool

    console.log(domain, bool)

    const msg = JSON.stringify({
        domain,
        bool
    })

    const queue = 'website'

    amqp.connect('amqp://localhost', function(error0, connection) {
                if (error0) {
                throw error0;
                }

                connection.createChannel(function(error1, channel) {
                    if (error1) {
                        throw error1;
                    }

                    channel.assertQueue(queue, {
                    durable: false
                    });


                    channel.sendToQueue(queue, Buffer.from(msg));
                
                });

            });
            res.status(200).send();
})


app.listen(port,()=>{
    console.log("Server running on "+port)
})
