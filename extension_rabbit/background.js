
const allTags = ["Arts and Entertainment",
    "Autos and Vehicles",
    "Beauty and Fitness",
    "Books and Literature",
    "Business and Industry",
    "Career and Education",
    "Computer and electronics",
    "Finance",
    "Food and Drink",
    "Gambling",
    "Games",
    "Health",
    "Home and Garden",
    "Internet and Telecom",
    "Law and Government",
    "News and Media",
    "People and Society",
    "Pets and Animals",
    "Recreation and Hobbies",
    "Reference",
    "Science",
    "Shopping",
    "Sports",
    "Travel",
    "Adult"]


const allowedTags = [
"Books and Literature",
"Career and Education",
"Computer and electronics",
"Health",
"Internet and Telecom",
"Law and Government",
"News and Media",
"Reference",
"Science",]

const skipDomain = ["www.google.com",
"www.google.co.in",
"google.co.in",
"google.com",
"chrome",
]

function post(url){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.send();
}

function check(url)
{
    var domain = url.replace('http://','').replace('https://','').split(/[/?#]/)[0];

    console.log(domain)

    if(skipDomain.includes(domain))
    {
        console.log("Skipped")
        return
    }
        
    fetch("https://website-categorization-api.whoisxmlapi.com/api/v1?apiKey=at_6ET7IqGiCU7F6qrCZJmYWlrP5Oc8q&domainName="+encodeURI(domain)).then((res)=>{
        return res.json()
    }).then((data)=>{

        const cat = data['categories']

        var ok = true;

        // cat.forEach(element => {
        //     if(!allowedTags.includes(element))
        //     {
        //         ok=false;
        //         return;
        //     }
        // });

        console.log(domain)
        console.log(cat)
        console.log(ok)

        const url = decodeURIComponent('http://localhost:3001/website?domain=youtube.com&bool=true')   
        post(url)

           
        // fetch(decodeURIComponent('https://localhost:3001/website?domain=youtube.com&bool='+ok))


    }).catch((e)=>{
        console.log(e)
        return
    })
}

chrome.tabs.onActivated.addListener(function(){
    chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
    if(tabs[0])
    {
        var url = tabs[0]['url']
        // check(url)
        console.log(url)
    }
})
})

chrome.tabs.onUpdated.addListener(function(tabId,changeInfo,tab) {
    if(changeInfo.url)
    {
        // alert(changeInfo.url)
        check(changeInfo.url)
        console.log(changeInfo) 
    }
});
